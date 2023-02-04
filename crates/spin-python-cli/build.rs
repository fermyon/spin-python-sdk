#![deny(warnings)]

use {
    anyhow::{bail, Result},
    std::{
        env,
        fs::{self, File},
        io::{self, Write},
        path::{Path, PathBuf},
    },
    tar::Builder,
    zstd::Encoder,
};

const ZSTD_COMPRESSION_LEVEL: i32 = 19;

fn main() -> Result<()> {
    println!("cargo:rerun-if-changed=build.rs");

    if let Ok("cargo-clippy") = env::var("CARGO_CFG_FEATURE").as_deref() {
        stubs_for_clippy()
    } else {
        package_engine_and_core_library()
    }
}

fn stubs_for_clippy() -> Result<()> {
    println!("cargo:warning=using stubbed engine and core library for static analysis purposes...");

    let engine_path = PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("engine.wasm.zst");

    if !engine_path.exists() {
        Encoder::new(File::create(engine_path)?, ZSTD_COMPRESSION_LEVEL)?.do_finish()?;
    }

    let core_library_path =
        PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("python-lib.tar.zst");

    if !core_library_path.exists() {
        Builder::new(Encoder::new(
            File::create(core_library_path)?,
            ZSTD_COMPRESSION_LEVEL,
        )?)
        .into_inner()?
        .do_finish()?;
    }

    Ok(())
}

fn package_engine_and_core_library() -> Result<()> {
    let override_engine_path = env::var_os("SPIN_PYTHON_ENGINE_PATH");
    let engine_path = if let Some(path) = override_engine_path {
        PathBuf::from(path)
    } else {
        let mut path = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").unwrap());
        path.pop();
        path.pop();
        path.join("target/wasm32-wasi/release/spin_python_engine.wasm")
    };

    println!("cargo:rerun-if-changed={engine_path:?}");

    if engine_path.exists() {
        let copied_engine_path =
            PathBuf::from(env::var("OUT_DIR").unwrap()).join("engine.wasm.zst");

        let mut encoder = Encoder::new(File::create(copied_engine_path)?, ZSTD_COMPRESSION_LEVEL)?;
        io::copy(&mut File::open(engine_path)?, &mut encoder)?;
        encoder.do_finish()?;
    } else {
        bail!("no such file: {}", engine_path.display())
    }

    let override_core_library_path = env::var_os("SPIN_PYTHON_CORE_LIBRARY_PATH");
    let core_library_path = if let Some(path) = override_core_library_path {
        PathBuf::from(path)
    } else {
        let mut path = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").unwrap());
        path.pop();
        path.pop();
        path.join("cpython/builddir/wasi/install/lib/python3.11")
    };

    println!("cargo:rerun-if-changed={core_library_path:?}");

    if core_library_path.exists() {
        let copied_core_library_path =
            PathBuf::from(env::var("OUT_DIR").unwrap()).join("python-lib.tar.zst");

        let mut builder = Builder::new(Encoder::new(
            File::create(copied_core_library_path)?,
            ZSTD_COMPRESSION_LEVEL,
        )?);

        add(&mut builder, &core_library_path, &core_library_path)?;

        builder.into_inner()?.do_finish()?;
    } else {
        bail!("no such directory: {}", core_library_path.display())
    }

    Ok(())
}

fn include(path: &Path) -> bool {
    !(matches!(
        path.extension().and_then(|e| e.to_str()),
        Some("a" | "pyc" | "whl")
    ) || matches!(
        path.file_name().and_then(|e| e.to_str()),
        Some("Makefile" | "Changelog" | "NEWS.txt")
    ))
}

fn add(builder: &mut Builder<impl Write>, root: &Path, path: &Path) -> Result<()> {
    if path.is_dir() {
        for entry in fs::read_dir(path)? {
            add(builder, root, &entry?.path())?;
        }
    } else if include(path) {
        builder.append_file(path.strip_prefix(root)?, &mut File::open(path)?)?;
    }

    Ok(())
}
