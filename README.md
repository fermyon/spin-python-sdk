# spin-python-sdk

This is an experiment to build a Spin Python SDK using CPython, Wizer, and PyO3.

## Prerequisites

- [WASI SDK](https://github.com/WebAssembly/wasi-sdk) v16 or later, installed in /opt/wasi-sdk
- [CPython](https://github.com/python/cpython) build prereqs (e.g. Make, Clang, etc.)
- [Rust](https://rustup.rs/) (including `wasm32-wasi` target)
- [Spin](https://github.com/fermyon/spin)
- [pipenv](https://pypi.org/project/pipenv/) for installing Python project dependencies

## Installing the Plugin and Running Examples

Use the following command to install the `py2wasm` plugin and then build the spin app:

```
spin plugins update
spin plugins install py2wasm
cd examples/hello world
spin build
spin up
```

## Building and Running

First, build CPython for wasm32-wasi:

```
git submodule update --init --recursive
mkdir -p cpython/builddir/wasi
mkdir -p cpython/builddir/build
cd cpython/builddir/build
../../configure --prefix=$(pwd)/install --enable-optimizations
make
cd ../wasi
CONFIG_SITE=../../Tools/wasm/config.site-wasm32-wasi ../../Tools/wasm/wasi-env \
    ../../configure -C --host=wasm32-unknown-wasi --build=$(../../config.guess) \
        --with-build-python=$(pwd)/../build/python --prefix=$(pwd)/install --disable-test-modules
make
make install
cd ../../..
```

Then, build the `spin-python-cli`:

```
make
```

Finally, build and run the example app:

```
cd examples/hello_world
../../target/release/spin-python app -o app.wasm
spin up
```

**Note:* `spin-python` and `py2wasm` are just different names for the same command. `spin-python` is used in the context of running the binary in a standalone context while `py2wasm` is  used when the command is run via Spin. In the samples provided in the `examples` directory, the `spin build` command depends on the plugin `py2wasm` being installed. Therefore, to test the locally built `spin-python` binary, replace the build command in the `spin.toml` to invoke it using spin build.

```
[component.build]
command = "../../target/release/spin-python app -o app.wasm"
```
