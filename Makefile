WASI_SDK_PATH ?= /opt/wasi-sdk

.PHONY: build
build: target/config.txt
	PYO3_CONFIG_FILE=$$(pwd)/target/config.txt cargo build --release --target=wasm32-wasi
	env -i PYTHONUNBUFFERED=1 \
		PYTHONHOME=/python \
		PYTHONPATH=/python:/py:/site-packages \
		$$(which wizer) \
		target/wasm32-wasi/release/python_wasi.wasm \
		--inherit-env true \
		--wasm-bulk-memory true \
		--allow-wasi \
		--dir py \
		--mapdir python::$$(pwd)/cpython/builddir/wasi/install/lib/python3.11 \
		--mapdir site-packages::$$(cd py && find $$(pipenv --venv)/lib -name site-packages | head -1) \
		-o target/wasm32-wasi/release/python-wasi-wizer.wasm

target/config.txt:
	mkdir -p target
	cp config.txt target
	echo "lib_dir=$$(pwd)/cpython/builddir/wasi" >> $@
