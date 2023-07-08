# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.224.2/containers/rust/.devcontainer/base.Dockerfile

# [Choice] Debian OS version (use bullseye on local arm64/Apple Silicon): buster, bullseye
ARG VARIANT="bullseye"

FROM mcr.microsoft.com/vscode/devcontainers/rust:0-${VARIANT}

ARG VARIANT

ARG WASI_VERSION="16"

ARG SPIN_VERSION="canary"

ENV WASI_VERSION_FULL=${WASI_VERSION}.0

# [Optional] Uncomment this section to install additional packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# Install rust components
RUN rustup update stable \
    && rustup default stable \
    && rustup component add clippy rustfmt \
    && rustup target add wasm32-wasi wasm32-unknown-unknown

# Install cPython build dependencies
RUN echo "deb-src http://deb.debian.org/debian $VARIANT main" >> /etc/apt/sources.list \
    && sudo apt-get update \
    && sudo apt-get -y build-dep python3 \
    && sudo apt-get -y install pkg-config

# Install WASI-SDK
RUN cd /tmp \
    && wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${WASI_VERSION}/wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
    && tar xvf wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
    && sudo cp -r wasi-sdk-${WASI_VERSION_FULL} /opt/wasi-sdk \
    && cd - 

# Install Spin
RUN cd /tmp \
    && git clone -b $SPIN_VERSION https://github.com/fermyon/spin \
    && cd spin \
    && make build \
    && cp ./target/release/spin /usr/local/bin
