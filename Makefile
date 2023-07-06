WASI_SDK_PATH ?= /opt/wasi-sdk
CARGO_TARGET_DIR ?= $(shell pwd)/target

$(CARGO_TARGET_DIR)/release/spin-python: \
		$(CARGO_TARGET_DIR)/wasm32-wasi/release/spin_python_engine.wasm \
		crates/spin-python-cli/build.rs \
		crates/spin-python-cli/src/main.rs
	cd crates/spin-python-cli && \
	SPIN_PYTHON_ENGINE_PATH=$< \
	SPIN_PYTHON_CORE_LIBRARY_PATH=$$(pwd)/../../cpython/builddir/wasi/install/lib/python3.11 \
	cargo build --release $(BUILD_TARGET)

$(CARGO_TARGET_DIR)/wasm32-wasi/release/spin_python_engine.wasm: \
		crates/spin-python-engine/src/lib.rs \
		crates/spin-python-engine/build.rs \
		$(CARGO_TARGET_DIR)/pyo3-config.txt
	cd crates/spin-python-engine && \
	PYO3_CONFIG_FILE=$(CARGO_TARGET_DIR)/pyo3-config.txt \
	cargo build --release --target=wasm32-wasi

$(CARGO_TARGET_DIR)/pyo3-config.txt: crates/spin-python-engine/pyo3-config.txt
	mkdir -p $(CARGO_TARGET_DIR)
	cp $< $(CARGO_TARGET_DIR)
	if which cygpath > /dev/null; then \
	echo "lib_dir=$$(cygpath -w $$(pwd)/cpython/builddir/wasi)" >> $@; \
	else \
	echo "lib_dir=$$(pwd)/cpython/builddir/wasi" >> $@; \
	fi
