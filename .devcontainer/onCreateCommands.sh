#!/bin/bash

set -ex
ARTIFACT_PY_VERSION="3.11.4"
ARTIFACT_SDK_VERSION="16"


# Install rust components
rustup update stable
rustup default stable
rustup component add clippy rustfmt
rustup target add wasm32-wasi wasm32-unknown-unknown

# Fetch WASI compiled cPython artifact
mkdir -p cpython/builddir/wasi/install

cd cpython/builddir/wasi/install
wget https://github.com/brettcannon/cpython-wasi-build/releases/download/v${ARTIFACT_PY_VERSION}/python-${ARTIFACT_PY_VERSION}-wasi_sdk-${ARTIFACT_SDK_VERSION}.zip
unzip python-${ARTIFACT_PY_VERSION}-wasi_sdk-${ARTIFACT_SDK_VERSION}.zip

cd -
cd cpython/builddir/wasi
wget https://github.com/brettcannon/cpython-wasi-build/releases/download/v${ARTIFACT_PY_VERSION}/_build-python-${ARTIFACT_PY_VERSION}-wasi_sdk-${ARTIFACT_SDK_VERSION}.zip
unzip _build-python-${ARTIFACT_PY_VERSION}-wasi_sdk-${ARTIFACT_SDK_VERSION}.zip
cd -

# Make Spin Python SDK
make