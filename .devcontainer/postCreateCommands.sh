#!/bin/bash

set -ex

# Install spin
cd /tmp
curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash
sudo mv ./spin /usr/local/bin/spin
cd /workspaces/spin-python-sdk

# Build cPython for wasm32
git submodule update --init --recursive
mkdir -p cpython/builddir/wasi
mkdir -p cpython/builddir/build
cd cpython/builddir/build
../../configure --prefix=$(pwd)/install --enable-optimizations
make -j$(nproc) -s
cd ../wasi
CONFIG_SITE=../../Tools/wasm/config.site-wasm32-wasi ../../Tools/wasm/wasi-env \
    ../../configure -C --host=wasm32-unknown-wasi --build=$(../../config.guess) \
        --with-build-python=$(pwd)/../build/python --prefix=$(pwd)/install --disable-test-modules
make -j$(nproc) -s
make install
cd ../../..
