#![deny(warnings)]

use {
    anyhow::{Error, Result},
    http::{header::HeaderName, request, HeaderValue},
    once_cell::unsync::OnceCell,
    pyo3::{exceptions::PyAssertionError, types::PyModule, PyErr, PyObject, PyResult, Python},
    spin_sdk::{
        http::{Request, Response},
        outbound_http,
    },
    std::{ops::Deref, str},
};

thread_local! {
    static HANDLE_REQUEST: OnceCell<PyObject> = OnceCell::new();
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
    // todo: this should be a byte slice, but make sure it gets converted to/from Python correctly
    #[pyo3(get, set)]
    body: Option<String>,
}

#[pyo3::pymethods]
impl HttpRequest {
    #[new]
    fn new(
        method: String,
        uri: String,
        headers: Vec<(String, String)>,
        body: Option<String>,
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
    // todo: this should be a byte slice, but make sure it gets converted to/from Python correctly
    #[pyo3(get, set)]
    body: Option<String>,
}

#[pyo3::pymethods]
impl HttpResponse {
    #[new]
    fn new(status: u16, headers: Vec<(String, String)>, body: Option<String>) -> Self {
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
fn send(request: HttpRequest) -> Result<HttpResponse, Anyhow> {
    let mut builder = request::Builder::new()
        .method(request.method.deref())
        .uri(request.uri.deref());

    if let Some(headers) = builder.headers_mut() {
        for (key, value) in &request.headers {
            headers.insert(
                HeaderName::from_bytes(key.as_bytes())?,
                HeaderValue::from_bytes(value.as_bytes())?,
            );
        }
    }

    let response = outbound_http::send_request(
        builder.body(request.body.map(|buffer| buffer.into_bytes().into()))?,
    )?;

    Ok(HttpResponse {
        status: response.status().as_u16(),
        headers: response
            .headers()
            .iter()
            .map(|(key, value)| {
                Ok((
                    key.as_str().to_owned(),
                    str::from_utf8(value.as_bytes())?.to_owned(),
                ))
            })
            .collect::<Result<_, Anyhow>>()?,
        body: response
            .into_body()
            .map(|bytes| String::from_utf8_lossy(&bytes).into_owned()),
    })
}

#[pyo3::pymodule]
#[pyo3(name = "spin_http")]
fn spin_http_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
    module.add_function(pyo3::wrap_pyfunction!(send, module)?)?;
    module.add_class::<HttpRequest>()?;
    module.add_class::<HttpResponse>()
}

fn do_init() -> Result<()> {
    pyo3::append_to_inittab!(spin_http_module);

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
                    str::from_utf8(v.as_bytes())?.to_owned(),
                ))
            })
            .collect::<Result<_>>()?,
        body: request
            .body()
            .as_ref()
            .map(|bytes| Ok::<_, Error>(str::from_utf8(bytes)?.to_owned()))
            .transpose()?,
    };

    let response = Python::with_gil(|py| {
        HANDLE_REQUEST.with(|cell| {
            cell.get()
                .unwrap()
                .call1(py, (request,))?
                .extract::<HttpResponse>(py)
        })
    })?;

    let mut builder = http::Response::builder().status(response.status);
    if let Some(headers) = builder.headers_mut() {
        for (key, value) in &response.headers {
            headers.insert(
                HeaderName::try_from(key.deref())?,
                HeaderValue::from_bytes(value.as_bytes())?,
            );
        }
    }

    Ok(builder.body(response.body.map(|buffer| buffer.into()))?)
}
