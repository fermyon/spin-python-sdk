#!/bin/bash

set -euo pipefail

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
 EXE=python
elif [[ "$OSTYPE" == "darwin"* ]]; then
  EXE=python.exe
else
  echo "This script does not support $OSTYPE"
fi

mkdir -p cpython/builddir/wasi cpython/builddir/build
pushd cpython/builddir/build
../../configure --prefix=$(pwd)/install --enable-optimizations
make
popd

pushd cpython/builddir/wasi
CONFIG_SITE=../../Tools/wasm/config.site-wasm32-wasi ../../Tools/wasm/wasi-env \
    ../../configure -C --host=wasm32-unknown-wasi --build=$(../../config.guess) \
    --with-build-python=$(pwd)/../build/$EXE --prefix=$(pwd)/install --disable-test-modules
make
make install
popd
