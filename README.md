# spin-python-sdk

This is an experiment to build a Spin Python SDK using CPython, Wizer, and PyO3.

## Installing the Plugin

Use the following command to install the `py2wasm` plugin and then build the example Spin app:

```bash
spin plugins update
spin plugins install py2wasm
```

If you'd like to try out the latest features, you can use the following command to install the *unstable* canary version of the plugin:

```bash
spin plugins install --url https://github.com/fermyon/spin-python-sdk/releases/download/canary/py2wasm.json
```

## [API Documentation](https://fermyon.github.io/spin-python-sdk)
 
## Running Examples

After installing the plugin, you can run the examples found in this repo.

__Note__: These examples track Spin's `main` branch, so you may need to ensure you are using the [canary](https://github.com/fermyon/spin/releases/tag/canary) Spin release.  See https://developer.fermyon.com/spin/install.



```bash
cd examples/hello world
spin build
spin up
```

## Building and Running

### Prerequisites
__Note__: When using the devcontainer for development, the following dependencies are already installed for you. To prevent speed up build times and prevent compatibility issues, a pre-compiled artifact of cpython for wasi is used rather than compiling from source. (https://github.com/brettcannon/cpython-wasi-build/releases/tag/v3.11.4)

- [WASI SDK](https://github.com/WebAssembly/wasi-sdk) v16 or later, installed in /opt/wasi-sdk
- [CPython](https://github.com/python/cpython) build prereqs (e.g. Make, Clang, etc.)
- [Rust](https://rustup.rs/) (including `wasm32-wasi` target)
- [Spin](https://github.com/fermyon/spin)
- [pipenv](https://pypi.org/project/pipenv/) for installing Python project dependencies


### Instructions

First, perform a git submodule update to update the cpython submodule. **(Unnecessary if using devcontainer)**
```bash
git submodule update --init --recursive
```

Then, build CPython for wasm32-wasi. **(Unnecessary if using devcontainer)**

```bash
./build-python.sh
```

Then, build the `spin-python-cli`: **(Unnecessary if using devcontainer)**

```bash
make
```

Finally, build and run the example app:

```bash
cd examples/hello_world
$CARGO_TARGET_DIR/release/spin-python app -o app.wasm
spin up
```

**Note:* `spin-python` and `py2wasm` are just different names for the same command. `spin-python` is used in the context of running the binary in a standalone context while `py2wasm` is  used when the command is run via Spin. In the samples provided in the `examples` directory, the `spin build` command depends on the plugin `py2wasm` being installed. Therefore, to test the locally built `spin-python` binary, replace the build command in the `spin.toml` to invoke it using `spin build`.

```
[component.build]
command = "$CARGO_TARGET_DIR/release/spin-python app -o app.wasm"
```
