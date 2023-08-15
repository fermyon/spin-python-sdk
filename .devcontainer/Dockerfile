# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.224.2/containers/rust/.devcontainer/base.Dockerfile

# [Choice] Debian OS version (use bullseye on local arm64/Apple Silicon): buster, bullseye
ARG VARIANT="bullseye"

FROM mcr.microsoft.com/vscode/devcontainers/rust:0-${VARIANT}

ARG VARIANT

ARG WASI_VERSION="16"

ENV WASI_VERSION_FULL=${WASI_VERSION}.0

# [Optional] Uncomment this section to install additional packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# Install rust components
RUN echo -e "${GREEN_COLOR}Installing Rust components...${RESET_COLOR}" \
    && rustup update stable \
    && rustup default stable \
    && rustup component add clippy rustfmt \
    && rustup target add wasm32-wasi wasm32-unknown-unknown \
    && echo -e "${GREEN_COLOR}Rust components installed.${RESET_COLOR}"

# Install cPython build dependencies
RUN echo -e "${GREEN_COLOR}Installing cPython build dependencies...${RESET_COLOR}" \
    && echo "deb-src http://deb.debian.org/debian $VARIANT main" >> /etc/apt/sources.list \
    && sudo apt-get update \
    && sudo apt-get -y build-dep python3 \
    && sudo apt-get -y install pkg-config \
    && echo -e "${GREEN_COLOR}cPython build dependencies installed.${RESET_COLOR}"

# Install WASI-SDK
RUN echo -e "${GREEN_COLOR}Installing WASI-SDK ${WASI_VERSION}...${RESET_COLOR}" \
    && cd /tmp \
    && wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${WASI_VERSION}/wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
    && tar xvf wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
    && sudo cp -r wasi-sdk-${WASI_VERSION_FULL} /opt/wasi-sdk \
    && cd - \
    && echo -e "${GREEN_COLOR}WASI-SDK installed.${RESET_COLOR}"

# Install Spin
RUN echo -e "${GREEN_COLOR}Installing Spin...${RESET_COLOR}" \
    && cd /tmp \ 
    && curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash \
    && sudo mv ./spin /usr/local/bin/spin \
    && cd -
    && echo -e "${GREEN_COLOR}Spin installed.${RESET_COLOR}"
