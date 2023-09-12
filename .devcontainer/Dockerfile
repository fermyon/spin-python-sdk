
ARG VARIANT="bullseye"

FROM mcr.microsoft.com/devcontainers/base:$VARIANT

ARG VARIANT

ARG WASI_VERSION="16"

ENV WASI_VERSION_FULL=${WASI_VERSION}.0

# [Optional] Uncomment this section to install additional packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# Install WASI-SDK
RUN cd /tmp \
&& wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${WASI_VERSION}/wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
&& tar xvf wasi-sdk-${WASI_VERSION_FULL}-linux.tar.gz \
&& sudo cp -r wasi-sdk-${WASI_VERSION_FULL} /opt/wasi-sdk \
&& cd -

# Install Spin
RUN cd /tmp \ 
&& curl -fsSL https://developer.fermyon.com/downloads/install.sh | bash \
&& sudo mv ./spin /usr/local/bin/spin \
&& cd -
