# spin-python-sdk

This is an experiment to build a Spin Python SDK using CPython, Wizer, and PyO3.

## Installing the Plugin and Running Examples

Use the following command to install the `py2wasm` plugin and then build the example Spin app:

```
spin plugins update
spin plugins install py2wasm
cd examples/hello world
spin build
spin up
```

## Building and Running

### Prerequisites

- [WASI SDK](https://github.com/WebAssembly/wasi-sdk) v16 or later, installed in /opt/wasi-sdk
- [CPython](https://github.com/python/cpython) build prereqs (e.g. Make, Clang, etc.)
- [Rust](https://rustup.rs/) (including `wasm32-wasi` target)
- [Spin](https://github.com/fermyon/spin)
- [pipenv](https://pypi.org/project/pipenv/) for installing Python project dependencies

### Instructions

First, build CPython for wasm32-wasi.

```bash
./build-python.sh
```

Then, build the `spin-python-cli`:

```
make
```

Finally, build and run the example app:

```
cd examples/hello_world
$CARGO_TARGET_DIR/release/spin-python app -o app.wasm
spin up
```

**Note:* `spin-python` and `py2wasm` are just different names for the same command. `spin-python` is used in the context of running the binary in a standalone context while `py2wasm` is  used when the command is run via Spin. In the samples provided in the `examples` directory, the `spin build` command depends on the plugin `py2wasm` being installed. Therefore, to test the locally built `spin-python` binary, replace the build command in the `spin.toml` to invoke it using `spin build`.

```
[component.build]
command = "$CARGO_TARGET_DIR/release/spin-python app -o app.wasm"
```
