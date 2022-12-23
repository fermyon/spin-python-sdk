#![deny(warnings)]

use {
    anyhow::{Error, Result},
    http::{header::HeaderName, HeaderValue},
    once_cell::unsync::OnceCell,
    pyo3::{FromPyObject, IntoPy, PyErr, PyObject, Python},
    spin_sdk::http::{Request, Response},
    std::{ops::Deref, str},
};

thread_local! {
    static REQUEST: OnceCell<PyObject> = OnceCell::new();
    static HANDLE_REQUEST: OnceCell<PyObject> = OnceCell::new();
}

struct HttpRequest<'a> {
    method: &'a str,
    uri: &'a str,
    headers: Vec<(&'a str, &'a str)>,
    // todo: this should be a byte slice, but make sure it gets converted to/from Python correctly
    body: Option<&'a str>,
}

impl IntoPy<PyObject> for HttpRequest<'_> {
    fn into_py(self, py: Python<'_>) -> PyObject {
        REQUEST.with(|cell| {
            cell.get()
                .unwrap()
                .call1(py, (self.method, self.uri, self.headers, self.body))
                .unwrap()
        })
    }
}

#[derive(FromPyObject)]
struct HttpResponse {
    status: u16,
    headers: Vec<(String, String)>,
    // todo: this should be a byte slice, but make sure it gets converted to/from Python correctly
    body: Option<String>,
}

fn do_init() -> Result<()> {
    pyo3::prepare_freethreaded_python();

    Python::with_gil(|py| {
        REQUEST.with(|cell| {
            cell.set(py.import("spin_http")?.getattr("Request")?.into())
                .unwrap();

            Ok::<_, PyErr>(())
        })?;

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
        method: request.method().as_str(),
        uri: &uri,
        headers: request
            .headers()
            .iter()
            .map(|(k, v)| Ok((k.as_str(), str::from_utf8(v.as_bytes())?)))
            .collect::<Result<_>>()?,
        body: request
            .body()
            .as_ref()
            .map(|bytes| Ok::<_, Error>(str::from_utf8(bytes)?))
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
