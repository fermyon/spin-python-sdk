#![deny(warnings)]

use {
    anyhow::{anyhow, Error, Result},
    bytes::Bytes,
    http::{header::HeaderName, request, HeaderValue},
    once_cell::unsync::OnceCell,
    pyo3::{
        exceptions::PyAssertionError,
        types::{PyBytes, PyList, PyMapping, PyModule},
        Py, PyAny, PyErr, PyObject, PyResult, Python, ToPyObject,
    },
    spin_sdk::{
        config,
        http::{Request, Response},
        key_value, llm, outbound_http,
        redis::{self, RedisParameter, RedisResult},
        sqlite,
    },
    std::{collections::HashMap, env, ops::Deref, str, sync::Arc},
};

thread_local! {
    static HANDLE_REQUEST: OnceCell<PyObject> = OnceCell::new();
    static ENVIRON: OnceCell<Py<PyMapping>> = OnceCell::new();
}

#[export_name = "spin-sdk-language-python"]
extern "C" fn __spin_sdk_language() {}

fn bytes(py: Python<'_>, src: &[u8]) -> PyResult<Py<PyBytes>> {
    Ok(PyBytes::new_with(py, src.len(), |dst| {
        dst.copy_from_slice(src);
        Ok(())
    })?
    .into())
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "Request")]
struct HttpRequest {
    #[pyo3(get, set)]
    method: String,
    #[pyo3(get, set)]
    uri: String,
    #[pyo3(get, set)]
    headers: HashMap<String, String>,
    #[pyo3(get, set)]
    body: Option<Py<PyBytes>>,
}

#[pyo3::pymethods]
impl HttpRequest {
    #[new]
    fn new(
        method: String,
        uri: String,
        headers: HashMap<String, String>,
        body: Option<Py<PyBytes>>,
    ) -> Self {
        Self {
            method,
            uri,
            headers,
            body,
        }
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "Response")]
struct HttpResponse {
    #[pyo3(get, set)]
    status: u16,
    #[pyo3(get, set)]
    headers: HashMap<String, String>,
    #[pyo3(get, set)]
    body: Option<Py<PyBytes>>,
}

#[pyo3::pymethods]
impl HttpResponse {
    #[new]
    fn new(status: u16, headers: HashMap<String, String>, body: Option<Py<PyBytes>>) -> Self {
        Self {
            status,
            headers,
            body,
        }
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "Store")]
struct Store {
    inner: Arc<key_value::Store>,
}

#[pyo3::pymethods]
impl Store {
    fn get(&self, py: Python<'_>, key: String) -> PyResult<PyObject> {
        match self.inner.get(key) {
            Ok(v) => bytes(py, &v).map(PyObject::from),
            Err(key_value::Error::NoSuchKey) => Ok(py.None()),
            Err(e) => Err(PyErr::from(Anyhow::from(e))),
        }
    }

    fn set(&self, key: String, value: &PyBytes) -> Result<(), Anyhow> {
        self.inner.set(key, value.as_bytes()).map_err(Anyhow::from)
    }

    fn delete(&self, key: String) -> Result<(), Anyhow> {
        self.inner.delete(key).map_err(Anyhow::from)
    }

    fn exists(&self, key: String) -> Result<bool, Anyhow> {
        self.inner.exists(key).map_err(Anyhow::from)
    }

    fn get_keys(&self) -> Result<Vec<String>, Anyhow> {
        self.inner.get_keys().map_err(Anyhow::from)
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "SqliteConnection")]
struct SqliteConnection {
    inner: Arc<sqlite::Connection>,
}

#[pyo3::pymethods]
impl SqliteConnection {
    fn execute(
        &self,
        _py: Python<'_>,
        query: String,
        parameters: Vec<&PyAny>,
    ) -> PyResult<QueryResult> {
        let parameters = parameters
            .iter()
            .map(|v| {
                if let Ok(v) = v.extract::<i64>() {
                    Ok(sqlite::ValueParam::Integer(v))
                } else if let Ok(v) = v.extract::<f64>() {
                    Ok(sqlite::ValueParam::Real(v))
                } else if let Ok(v) = v.extract::<&str>() {
                    Ok(sqlite::ValueParam::Text(v))
                } else if v.is_none() {
                    Ok(sqlite::ValueParam::Null)
                } else if let Ok(v) = v.downcast::<PyBytes>() {
                    Ok(sqlite::ValueParam::Blob(v.as_bytes()))
                } else {
                    Err(PyErr::from(Anyhow(anyhow!(
                        "Unable to use {v:?} as a SQLite `execute` parameter \
                     -- expected `int`, `float`, `bytes`, `string`, or `None`"
                    ))))
                }
            })
            .collect::<PyResult<Vec<_>>>()?;
        let result = self
            .inner
            .execute(&query, &parameters)
            .map_err(Anyhow::from)?;
        Ok(QueryResult { inner: result })
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "QueryResult")]
struct QueryResult {
    inner: sqlite::QueryResult,
}

#[pyo3::pymethods]
impl QueryResult {
    fn rows(&self, py: Python<'_>) -> PyResult<PyObject> {
        let rows = self.inner.rows.iter().map(|r| {
            PyList::new(
                py,
                r.values.iter().map(|v| match v {
                    sqlite::ValueResult::Integer(i) => i.to_object(py),
                    sqlite::ValueResult::Real(r) => r.to_object(py),
                    sqlite::ValueResult::Text(s) => s.to_object(py),
                    sqlite::ValueResult::Blob(b) => b.to_object(py),
                    sqlite::ValueResult::Null => py.None(),
                }),
            )
        });
        Ok(PyList::new(py, rows).into())
    }

    fn columns(&self, py: Python<'_>) -> PyResult<PyObject> {
        Ok(PyList::new(py, self.inner.columns.iter()).into())
    }
}

struct Anyhow(Error);

impl From<Anyhow> for PyErr {
    fn from(Anyhow(error): Anyhow) -> Self {
        PyAssertionError::new_err(format!("{error:?}"))
    }
}

impl<T: std::error::Error + Send + Sync + 'static> From<T> for Anyhow {
    fn from(error: T) -> Self {
        Self(error.into())
    }
}

#[pyo3::pyfunction]
#[pyo3(pass_module)]
fn http_send(module: &PyModule, request: HttpRequest) -> PyResult<HttpResponse> {
    let mut builder = request::Builder::new()
        .method(request.method.deref())
        .uri(request.uri.deref());

    if let Some(headers) = builder.headers_mut() {
        for (key, value) in &request.headers {
            headers.insert(
                HeaderName::from_bytes(key.as_bytes()).map_err(Anyhow::from)?,
                HeaderValue::from_bytes(value.as_bytes()).map_err(Anyhow::from)?,
            );
        }
    }

    let response = outbound_http::send_request(
        builder
            .body(
                request
                    .body
                    .map(|buffer| Bytes::copy_from_slice(buffer.as_bytes(module.py()))),
            )
            .map_err(Anyhow::from)?,
    )
    .map_err(Anyhow::from)?;

    Ok(HttpResponse {
        status: response.status().as_u16(),
        headers: response
            .headers()
            .iter()
            .map(|(key, value)| {
                Ok((
                    key.as_str().to_owned(),
                    str::from_utf8(value.as_bytes())
                        .map_err(Anyhow::from)?
                        .to_owned(),
                ))
            })
            .collect::<PyResult<HashMap<_, _>>>()?,
        body: response
            .into_body()
            .as_deref()
            .map(|buffer| bytes(module.py(), buffer))
            .transpose()?,
    })
}

#[pyo3::pymodule]
#[pyo3(name = "spin_http")]
fn spin_http_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(http_send, module)?)?;
    module.add_class::<HttpRequest>()?;
    module.add_class::<HttpResponse>()
}

#[pyo3::pyfunction]
fn redis_del(address: String, keys: Vec<String>) -> PyResult<i64> {
    let keys = keys.iter().map(|s| s.as_str()).collect::<Vec<_>>();
    redis::del(&address, &keys)
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
}

#[pyo3::pyfunction]
#[pyo3(pass_module)]
fn redis_get(module: &PyModule, address: String, key: String) -> PyResult<Py<PyBytes>> {
    bytes(
        module.py(),
        &redis::get(&address, &key)
            .map_err(|_| Anyhow(anyhow!("Error executing Redis get command")))?,
    )
}

#[pyo3::pyfunction]
fn redis_incr(address: String, key: String) -> PyResult<i64> {
    redis::incr(&address, &key)
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis incr command"))))
}

#[pyo3::pyfunction]
fn redis_publish(address: String, channel: String, payload: &PyBytes) -> PyResult<()> {
    redis::publish(&address, &channel, payload.as_bytes())
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis publish command"))))
}

#[pyo3::pyfunction]
fn redis_sadd(address: String, key: String, values: Vec<String>) -> PyResult<i64> {
    let values = values.iter().map(|s| s.as_str()).collect::<Vec<_>>();
    redis::sadd(&address, &key, &values)
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
}

#[pyo3::pyfunction]
fn redis_set(address: String, key: String, value: &PyBytes) -> PyResult<()> {
    redis::set(&address, &key, value.as_bytes())
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
}

#[pyo3::pyfunction]
fn redis_smembers(address: String, key: String) -> PyResult<Vec<String>> {
    redis::smembers(&address, &key)
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
}

#[pyo3::pyfunction]
fn redis_srem(address: String, key: String, values: Vec<String>) -> PyResult<i64> {
    let values = values.iter().map(|s| s.as_str()).collect::<Vec<_>>();
    redis::srem(&address, &key, &values)
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
}

#[pyo3::pyfunction]
#[pyo3(pass_module)]
fn redis_execute(
    module: &PyModule,
    address: String,
    command: String,
    arguments: Vec<&PyAny>,
) -> PyResult<Vec<PyObject>> {
    let arguments = arguments
        .iter()
        .map(|v| {
            if let Ok(v) = v.extract::<i64>() {
                Ok(RedisParameter::Int64(v))
            } else if let Ok(v) = v.downcast::<PyBytes>() {
                Ok(RedisParameter::Binary(v.as_bytes()))
            } else {
                Err(PyErr::from(Anyhow(anyhow!(
                    "Unable to use {v:?} as a Redis `execute` argument \
                     -- expected `int` or `bytes`"
                ))))
            }
        })
        .collect::<PyResult<Vec<_>>>()?;

    redis::execute(&address, &command, &arguments)
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
        .and_then(|results| {
            results
                .into_iter()
                .map(|v| match v {
                    RedisResult::Nil => Ok(module.py().None()),
                    RedisResult::Status(v) => Ok(v.to_object(module.py())),
                    RedisResult::Int64(v) => Ok(v.to_object(module.py())),
                    RedisResult::Binary(v) => bytes(module.py(), &v).map(PyObject::from),
                })
                .collect::<PyResult<_>>()
        })
}

#[pyo3::pymodule]
#[pyo3(name = "spin_redis")]
fn spin_redis_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(redis_del, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_get, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_incr, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_publish, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_sadd, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_set, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_smembers, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_srem, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_execute, module)?)
}

#[pyo3::pyfunction]
fn kv_open(name: String) -> Result<Store, Anyhow> {
    Ok(Store {
        inner: Arc::new(key_value::Store::open(name).map_err(Anyhow::from)?),
    })
}

#[pyo3::pyfunction]
fn kv_open_default() -> Result<Store, Anyhow> {
    Ok(Store {
        inner: Arc::new(key_value::Store::open_default().map_err(Anyhow::from)?),
    })
}

#[pyo3::pymodule]
#[pyo3(name = "spin_key_value")]
fn spin_key_value_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(kv_open, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(kv_open_default, module)?)
}

#[pyo3::pyfunction]
fn sqlite_open(database: String) -> Result<SqliteConnection, Anyhow> {
    Ok(SqliteConnection {
        inner: Arc::new(sqlite::Connection::open(&database).map_err(Anyhow::from)?),
    })
}

#[pyo3::pyfunction]
fn sqlite_open_default() -> Result<SqliteConnection, Anyhow> {
    Ok(SqliteConnection {
        inner: Arc::new(sqlite::Connection::open_default().map_err(Anyhow::from)?),
    })
}

#[pyo3::pymodule]
#[pyo3(name = "spin_sqlite")]
fn spin_sqlite_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(sqlite_open, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(sqlite_open_default, module)?)
}

#[pyo3::pyfunction]
fn config_get(key: String) -> Result<String, Anyhow> {
    config::get(&key).map_err(Anyhow::from)
}

#[pyo3::pymodule]
#[pyo3(name = "spin_config")]
fn spin_config_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(config_get, module)?)
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "LLMInferencingUsage")]
struct LLMInferencingUsage {
    #[pyo3(get)]
    prompt_token_count: u32,
    #[pyo3(get)]
    generated_token_count: u32,
}

impl From<llm::InferencingUsage> for LLMInferencingUsage {
    fn from(result: llm::InferencingUsage) -> Self {
        LLMInferencingUsage {
            prompt_token_count: result.prompt_token_count,
            generated_token_count: result.generated_token_count,
        }
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "LLMInferencingResult")]
struct LLMInferencingResult {
    #[pyo3(get)]
    text: String,
    #[pyo3(get)]
    usage: LLMInferencingUsage,
}

impl From<llm::InferencingResult> for LLMInferencingResult {
    fn from(result: llm::InferencingResult) -> Self {
        LLMInferencingResult {
            text: result.text.clone(),
            usage: LLMInferencingUsage::from(result.usage),
        }
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "LLMInferencingParams")]
struct LLMInferencingParams {
    #[pyo3(get, set)]
    max_tokens: u32,
    #[pyo3(get, set)]
    repeat_penalty: f32,
    #[pyo3(get, set)]
    repeat_penalty_last_n_token_count: u32,
    #[pyo3(get, set)]
    temperature: f32,
    #[pyo3(get, set)]
    top_k: u32,
    #[pyo3(get, set)]
    top_p: f32,
}

#[pyo3::pymethods]
impl LLMInferencingParams {
    #[new]
    fn new(
        max_tokens: u32,
        repeat_penalty: f32,
        repeat_penalty_last_n_token_count: u32,
        temperature: f32,
        top_k: u32,
        top_p: f32,
    ) -> Self {
        Self {
            max_tokens,
            repeat_penalty,
            repeat_penalty_last_n_token_count,
            temperature,
            top_k,
            top_p,
        }
    }
}

impl From<LLMInferencingParams> for llm::InferencingParams {
    fn from(p: LLMInferencingParams) -> Self {
        llm::InferencingParams {
            max_tokens: p.max_tokens,
            repeat_penalty: p.repeat_penalty,
            repeat_penalty_last_n_token_count: p.repeat_penalty_last_n_token_count,
            temperature: p.temperature,
            top_k: p.top_k,
            top_p: p.top_p,
        }
    }
}

#[pyo3::pyfunction]
fn llm_infer(
    model: &str,
    prompt: &str,
    options: Option<LLMInferencingParams>,
) -> Result<LLMInferencingResult, Anyhow> {
    let m = match model {
        "llama2-chat" => llm::InferencingModel::Llama2Chat,
        "codellama-instruct" => llm::InferencingModel::CodellamaInstruct,
        _ => llm::InferencingModel::Other(model),
    };

    let opts = match options {
        Some(o) => llm::InferencingParams::from(o),
        _ => llm::InferencingParams::default(),
    };

    llm::infer_with_options(m, prompt, opts)
        .map_err(Anyhow::from)
        .map(LLMInferencingResult::from)
}

#[pyo3::pyfunction]
fn generate_embeddings(model: &str, text: Vec<String>) -> Result<LLMEmbeddingsResult, Anyhow> {
    let model = match model {
        "all-minilm-l6-v2" => llm::EmbeddingModel::AllMiniLmL6V2,
        _ => llm::EmbeddingModel::Other(model),
    };

    let text = text.iter().map(|s| s.as_str()).collect::<Vec<_>>();

    llm::generate_embeddings(model, &text)
        .map_err(Anyhow::from)
        .map(LLMEmbeddingsResult::from)
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "LLMEmbeddingsUsage")]
struct LLMEmbeddingsUsage {
    #[pyo3(get)]
    prompt_token_count: u32,
}

impl From<llm::EmbeddingsUsage> for LLMEmbeddingsUsage {
    fn from(result: llm::EmbeddingsUsage) -> Self {
        LLMEmbeddingsUsage {
            prompt_token_count: result.prompt_token_count,
        }
    }
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "LLMEmbeddingResult")]
struct LLMEmbeddingsResult {
    #[pyo3(get)]
    embeddings: Vec<Vec<f32>>,
    #[pyo3(get)]
    usage: LLMEmbeddingsUsage,
}

impl From<llm::EmbeddingsResult> for LLMEmbeddingsResult {
    fn from(result: llm::EmbeddingsResult) -> Self {
        LLMEmbeddingsResult {
            embeddings: result.embeddings,
            usage: LLMEmbeddingsUsage::from(result.usage),
        }
    }
}

#[pyo3::pymodule]
#[pyo3(name = "spin_llm")]
fn spin_llm_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(llm_infer, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(generate_embeddings, module)?)?;
    module.add_class::<LLMInferencingUsage>()?;
    module.add_class::<LLMInferencingParams>()?;
    module.add_class::<LLMInferencingResult>()?;
    module.add_class::<LLMEmbeddingsUsage>()?;
    module.add_class::<LLMEmbeddingsResult>()
}

pub fn run_ctors() {
    unsafe {
        extern "C" {
            fn __wasm_call_ctors();
        }
        __wasm_call_ctors();
    }
}

fn do_init() -> Result<()> {
    run_ctors();

    pyo3::append_to_inittab!(spin_http_module);
    pyo3::append_to_inittab!(spin_redis_module);
    pyo3::append_to_inittab!(spin_config_module);
    pyo3::append_to_inittab!(spin_key_value_module);
    pyo3::append_to_inittab!(spin_sqlite_module);
    pyo3::append_to_inittab!(spin_llm_module);

    pyo3::prepare_freethreaded_python();

    Python::with_gil(|py| {
        HANDLE_REQUEST.with(|cell| {
            cell.set(
                py.import(
                    env::var("SPIN_PYTHON_APP_NAME")
                        .map_err(Anyhow::from)?
                        .deref(),
                )?
                .getattr("handle_request")?
                .into(),
            )
            .unwrap();

            Ok::<_, PyErr>(())
        })?;

        ENVIRON.with(|cell| {
            let environ = py
                .import("os")?
                .getattr("environ")?
                .downcast::<PyMapping>()
                .unwrap();

            let keys = environ.keys()?;

            for i in 0..keys.len()? {
                environ.del_item(keys.get_item(i)?)?;
            }

            cell.set(environ.into()).unwrap();

            Ok(())
        })
    })
}

#[export_name = "wizer.initialize"]
pub extern "C" fn init() {
    do_init().unwrap();
}

#[spin_sdk::http_component]
fn handle(request: Request) -> Result<Response> {
    run_ctors();

    Python::with_gil(|py| {
        let uri = request.uri().to_string();

        let request = HttpRequest {
            method: request.method().as_str().to_owned(),
            uri,
            headers: request
                .headers()
                .iter()
                .try_fold::<_, _, PyResult<HashMap<_, _>>>(
                    HashMap::new(),
                    |mut acc: HashMap<String, String>, (k, v): (&HeaderName, &HeaderValue)| {
                        let key = k.as_str().to_owned();
                        let value = str::from_utf8(v.as_bytes())
                            .map_err(Anyhow::from)?
                            .to_owned();
                        acc.entry(key)
                            .and_modify(|existing_value| {
                                existing_value.push_str(", ");
                                existing_value.push_str(&value);
                            })
                            .or_insert(value);
                        Ok(acc)
                    },
                )
                .map_err(Anyhow::from)?,
            body: request
                .body()
                .as_deref()
                .map(|buffer| bytes(py, buffer))
                .transpose()?,
        };

        ENVIRON.with(|cell| {
            let environ = cell.get().unwrap().as_ref(py);

            for (k, v) in env::vars() {
                environ.set_item(k, v)?;
            }

            Ok::<(), PyErr>(())
        })?;

        let response = HANDLE_REQUEST.with(|cell| {
            cell.get()
                .unwrap()
                .call1(py, (request,))?
                .extract::<HttpResponse>(py)
        })?;

        let mut builder = http::Response::builder().status(response.status);
        if let Some(headers) = builder.headers_mut() {
            for (key, value) in &response.headers {
                headers.insert(
                    HeaderName::try_from(key.deref()).map_err(Anyhow::from)?,
                    HeaderValue::from_bytes(value.as_bytes()).map_err(Anyhow::from)?,
                );
            }
        }

        Ok::<_, PyErr>(
            builder
                .body(
                    response
                        .body
                        .map(|buffer| Bytes::copy_from_slice(buffer.as_bytes(py))),
                )
                .map_err(Anyhow::from)?,
        )
    })
    .map_err(Error::from)
}
