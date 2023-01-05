.PHONY: build
build: target/config.txt target/lib
	PYO3_CONFIG_FILE=$$(pwd)/target/config.txt cargo build --release --target=wasm32-wasi
	env -i wasi-vfs/target/release/wasi-vfs pack target/wasm32-wasi/release/python_wasi.wasm \
		--mapdir lib::$$(pwd)/target/lib \
		-o target/wasm32-wasi/release/python-wasi-vfs.wasm
	env -i PYTHONUNBUFFERED=1 PYTHONPATH=/py:/site-packages \
		$$(which wizer) target/wasm32-wasi/release/python-wasi-vfs.wasm \
		--inherit-env true --wasm-bulk-memory true --allow-wasi --dir py \
		--mapdir site-packages::$$(cd py && find $$(pipenv --venv)/lib -name site-packages | head -1) \
		-o target/wasm32-wasi/release/python-wasi-vfs-wizer.wasm

target/config.txt:
	mkdir -p target
	cp config.txt target
	echo "lib_dir=$$(pwd)/cpython/builddir/wasi" >> $@

target/lib:
	mkdir -p $@
	rsync -a --exclude='*.a' --exclude='*.pyc' --exclude='*.whl' --exclude=Makefile \
		--exclude=Changelog --exclude=NEWS.txt \
		cpython/builddir/wasi/install/lib/python3.11 $@
