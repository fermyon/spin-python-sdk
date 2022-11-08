## Building and Running

First, CPython:

```
git clone git@github.com:python/cpython
mkdir -p cpython/builddir/wasi
mkdir -p cpython/builddir/build
cd cpython/builddir/build
git checkout v3.11.0
../../configure --prefix=$(pwd)/install --enable-optimizations
make
cd ../wasi
CONFIG_SITE=../../Tools/wasm/config.site-wasm32-wasi ../../Tools/wasm/wasi-env \
    ../../configure -C --host=wasm32-unknown-wasi --build=$(../../config.guess) \
        --with-build-python=$(pwd)/../build/python --prefix=$(pwd)/install --disable-test-modules
make
make install
```

Then, this thing:

```
PYO3_CONFIG_FILE=$(pwd)/config.txt cargo build --release --target=wasm32-wasi
```

Finally, run:

```
wasmtime --mapdir /::../cpython/builddir/wasi/install/ --env PYTHONPATH=/lib/python3.11 \
    target/wasm32-wasi/release/python-wasi.wasm
```
