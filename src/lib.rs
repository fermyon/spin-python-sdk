#![deny(warnings)]

use {
    anyhow::{Error, Result},
    http::{header::HeaderName, HeaderValue},
    once_cell::unsync::OnceCell,
    pyo3::{types::PyModule, PyObject, PyResult, Python},
    spin_sdk::http::{Request, Response},
    std::{ops::Deref, str},
};

thread_local! {
    static HANDLE_REQUEST: OnceCell<PyObject> = OnceCell::new();
}

#[pyo3::pyclass]
#[pyo3(name = "Request")]
struct HttpRequest {
    #[pyo3(get)]
    method: String,
    #[pyo3(get)]
    uri: String,
    #[pyo3(get)]
    headers: Vec<(String, String)>,
    // todo: this should be a byte slice, but make sure it gets converted to/from Python correctly
    #[pyo3(get)]
    body: Option<String>,
}

#[derive(Clone)]
#[pyo3::pyclass]
#[pyo3(name = "Response")]
struct HttpResponse {
    status: u16,
    headers: Vec<(String, String)>,
    // todo: this should be a byte slice, but make sure it gets converted to/from Python correctly
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

#[pyo3::pymodule]
#[pyo3(name = "spin_http")]
fn spin_http_module(_py: Python<'_>, module: &PyModule) -> PyResult<()> {
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
