use pyo3::{
    prelude::{PyResult, Python},
    types::IntoPyDict,
};

fn main() -> PyResult<()> {
    // Force `wasi_vfs_pack_fs` to be linked in and exported so `wasi-vfs-cli` can do its thing:
    std::hint::black_box(wasi_vfs::__internal_wasi_vfs_rt_init);

    pyo3::prepare_freethreaded_python();

    Python::with_gil(|py| {
        let sys = py.import("sys")?;
        let version: String = sys.getattr("version")?.extract()?;

        let locals = [("os", py.import("os")?)].into_py_dict(py);
        let code = "os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'";
        let user: String = py.eval(code, None, Some(locals))?.extract()?;

        println!("Hello {}, I'm Python {}", user, version);
        Ok(())
    })
}
