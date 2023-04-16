#![deny(warnings)]

use {
    anyhow::{anyhow, Error, Result},
    bytes::Bytes,
    http::{header::HeaderName, request, HeaderValue},
    once_cell::unsync::OnceCell,
    pyo3::{
        exceptions::PyAssertionError,
        types::{PyBytes, PyMapping, PyModule},
        Py, PyAny, PyErr, PyObject, PyResult, Python, ToPyObject,
    },
    spin_sdk::{
        config,
        http::{Request, Response},
        key_value, outbound_http,
        redis::{self, RedisParameter, RedisResult},
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
fn config_get(key: String) -> Result<String, Anyhow> {
    config::get(&key).map_err(Anyhow::from)
}

#[pyo3::pymodule]
#[pyo3(name = "spin_config")]
fn spin_config_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(config_get, module)?)
}

fn do_init() -> Result<()> {
    pyo3::append_to_inittab!(spin_http_module);
    pyo3::append_to_inittab!(spin_redis_module);
    pyo3::append_to_inittab!(spin_config_module);
    pyo3::append_to_inittab!(spin_key_value_module);

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
    Python::with_gil(|py| {
        let uri = request.uri().to_string();

        let request = HttpRequest {
            method: request.method().as_str().to_owned(),
            uri,
            headers: request
                .headers()
                .iter()
                .map(|(k, v)| {
                    Ok((
                        k.as_str().to_owned(),
                        str::from_utf8(v.as_bytes())
                            .map_err(Anyhow::from)?
                            .to_owned(),
                    ))
                })
                .collect::<PyResult<HashMap<_, _>>>()?,
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
