#![deny(warnings)]

use {
    anyhow::{bail, Context, Result},
    clap::Parser,
    std::{
        env, fs,
        io::Cursor,
        path::{Path, PathBuf},
        process::Command,
        str,
    },
    tar::Archive,
    wizer::Wizer,
    zstd::Decoder,
};

/// A Spin plugin to convert Python apps to Spin-compatible WebAssembly modules
#[derive(Parser, Debug)]
#[command(author, version, about)]
struct Options {
    /// The name of a Python module containing a `handle_request` function for handling Spin HTTP requests
    app_name: String,

    /// `PYTHONPATH` for specifying directory containing the app and optionally other directories containing
    /// dependencies.
    ///
    /// If `pipenv` is in `PATH` and `pipenv --venv` produces a path containing a `site-packages` subdirectory,
    /// that directory will be appended to this value as a convenience for `pipenv` users.
    #[arg(short = 'p', long, default_value = ".")]
    python_path: String,

    /// Output file to write the resulting module to
    #[arg(short = 'o', long, default_value = "index.wasm")]
    output: PathBuf,
}

#[derive(Parser, Debug)]
struct PrivateOptions {
    app_name: String,
    python_home: String,
    python_path: String,
    output: PathBuf,
}

fn main() -> Result<()> {
    if env::var_os("SPIN_PYTHON_WIZEN").is_some() {
        let options = PrivateOptions::parse();

        env::remove_var("SPIN_PYTHON_WIZEN");

        env::set_var("PYTHONUNBUFFERED", "1");
        env::set_var("SPIN_PYTHON_APP_NAME", &options.app_name);

        let mut wizer = Wizer::new();

        wizer
            .allow_wasi(true)?
            .inherit_env(true)
            .inherit_stdio(true)
            .wasm_bulk_memory(true);

        let python_path = options
            .python_path
            .split(':')
            .enumerate()
            .map(|(index, path)| {
                let index = index.to_string();
                wizer.map_dir(&index, path);
                format!("/{index}")
            })
            .collect::<Vec<_>>()
            .join(":");

        wizer.map_dir("python", &options.python_home);

        env::set_var("PYTHONPATH", &format!("/python:{python_path}"));
        env::set_var("PYTHONHOME", "/python");

        fs::write(
            &options.output,
            wizer.run(&zstd::decode_all(Cursor::new(include_bytes!(concat!(
                env!("OUT_DIR"),
                "/engine.wasm.zstd"
            ))))?)?,
        )?;
    } else {
        let options = Options::parse();

        let temp = tempfile::tempdir()?;

        Archive::new(Decoder::new(Cursor::new(include_bytes!(concat!(
            env!("OUT_DIR"),
            "/python-lib.tar.zstd"
        ))))?)
        .unpack(temp.path())?;

        let mut python_path = options.python_path;
        if let Some(site_packages) = find_site_packages()? {
            python_path = format!(
                "{python_path}:{}",
                site_packages
                    .to_str()
                    .context("non-UTF-8 site-packages name")?
            )
        }

        let status = Command::new(env::args().next().unwrap())
            .env_clear()
            .env("SPIN_PYTHON_WIZEN", "1")
            .arg(&options.app_name)
            .arg(
                &temp
                    .path()
                    .to_str()
                    .context("non-UTF-8 temporary directory name")?,
            )
            .arg(&python_path)
            .arg(&options.output)
            .status()?;

        if !status.success() {
            bail!("Couldn't create wasm from input");
        }

        println!("Spin-compatible module built successfully");
    }

    Ok(())
}

fn find_site_packages() -> Result<Option<PathBuf>> {
    Ok(match Command::new("pipenv").arg("--venv").output() {
        Ok(output) => {
            if !output.status.success() {
                bail!(
                    "Error running pipenv: {}",
                    String::from_utf8_lossy(&output.stderr)
                );
            }

            let dir = str::from_utf8(&output.stdout)?.trim();

            if let Some(site_packages) = find("site-packages", &Path::new(dir).join("lib"))? {
                Some(site_packages)
            } else {
                eprintln!("warning: site-packages directory not found under {dir}");
                None
            }
        }
        Err(_) => None,
    })
}

fn find(name: &str, path: &Path) -> Result<Option<PathBuf>> {
    if path.is_dir() {
        match path.file_name().and_then(|name| name.to_str()) {
            Some(this_name) if this_name == name => {
                return Ok(Some(path.canonicalize()?));
            }
            _ => {
                for entry in fs::read_dir(path)? {
                    if let Some(path) = find(name, &entry?.path())? {
                        return Ok(Some(path));
                    }
                }
            }
        }
    }

    Ok(None)
}
