# python-wasi

This is an experiment to build the CPython interpreter as a self-contained,
WASI-enabled Wasm module with Rust interopability.

## Prerequisites

- CPython build prereqs (e.g. Make, Clang, etc.)
- Rust (including `wasm32-wasi` target)
- [wasi-sdk](https://github.com/WebAssembly/wasi-sdk) v16 or later

## Building and Running

First, CPython:

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

Then, this project:

```
mkdir -p target
cat > target/config.txt <<EOF
implementation=CPython
version=3.11
shared=false
abi3=true
lib_name=python3.11
pointer_width=32
build_flags=
suppress_build_script_link_lines=false
lib_dir=$(pwd)/cpython/builddir/wasi
EOF
PYO3_CONFIG_FILE=$(pwd)/target/config.txt cargo build --release --target=wasm32-wasi
```

Pack the CPython lib directory into the module using `wasi-vfs`:

```
(cd wasi-vfs && cargo build --release -p wasi-vfs-cli)
wasi-vfs/target/release/wasi-vfs pack target/wasm32-wasi/release/python-wasi.wasm --mapdir lib::$(pwd)/cpython/builddir/wasi/install/lib -o target/wasm32-wasi/release/python.wasm
```

Finally, run:

```
wasmtime target/wasm32-wasi/release/python-wasi.wasm
```
