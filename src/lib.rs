#![deny(warnings)]

use {
    anyhow::{anyhow, Error, Result},
    bytes::Bytes,
    http::{header::HeaderName, request, HeaderValue},
    once_cell::unsync::OnceCell,
    pyo3::{
        exceptions::PyAssertionError,
        types::{PyBytes, PyModule},
        Py, PyErr, PyObject, PyResult, Python,
    },
    spin_sdk::{
        config,
        http::{Request, Response},
        outbound_http, redis,
    },
    std::{ops::Deref, str},
};

thread_local! {
    static HANDLE_REQUEST: OnceCell<PyObject> = OnceCell::new();
}

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
    headers: Vec<(String, String)>,
    #[pyo3(get, set)]
    body: Option<Py<PyBytes>>,
}

#[pyo3::pymethods]
impl HttpRequest {
    #[new]
    fn new(
        method: String,
        uri: String,
        headers: Vec<(String, String)>,
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
    headers: Vec<(String, String)>,
    #[pyo3(get, set)]
    body: Option<Py<PyBytes>>,
}

#[pyo3::pymethods]
impl HttpResponse {
    #[new]
    fn new(status: u16, headers: Vec<(String, String)>, body: Option<Py<PyBytes>>) -> Self {
        Self {
            status,
            headers,
            body,
        }
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
            .collect::<PyResult<_>>()?,
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
#[pyo3(pass_module)]
fn redis_get(module: &PyModule, address: String, key: String) -> PyResult<Py<PyBytes>> {
    bytes(
        module.py(),
        &redis::get(&address, &key)
            .map_err(|_| Anyhow(anyhow!("Error executing Redis get command")))?,
    )
}

#[pyo3::pyfunction]
fn redis_set(address: String, key: String, value: &PyBytes) -> PyResult<()> {
    redis::set(&address, &key, value.as_bytes())
        .map_err(|_| PyErr::from(Anyhow(anyhow!("Error executing Redis set command"))))
}

#[pyo3::pymodule]
#[pyo3(name = "spin_redis")]
fn spin_redis_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(redis_get, module)?)?;
    module.add_function(pyo3::wrap_pyfunction!(redis_set, module)?)
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

    pyo3::prepare_freethreaded_python();

    Python::with_gil(|py| {
        HANDLE_REQUEST.with(|cell| {
            cell.set(py.import("app")?.getattr("handle_request")?.into())
                .unwrap();

            Ok(())
        })
    })
}

#[export_name = "wizer.initialize"]
pub extern "C" fn init() {
    std::hint::black_box(wasi_vfs::__internal_wasi_vfs_rt_init);

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
                .collect::<PyResult<_>>()?,
            body: request
                .body()
                .as_deref()
                .map(|buffer| bytes(py, buffer))
                .transpose()?,
        };

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
