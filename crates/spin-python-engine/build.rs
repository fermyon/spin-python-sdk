fn main() {
    let wasi_sdk_path =
        std::env::var("WASI_SDK_PATH").unwrap_or_else(|_| "/opt/wasi-sdk".to_owned());

    println!("cargo:rustc-link-search={wasi_sdk_path}/share/wasi-sysroot/lib/wasm32-wasi");
    println!("cargo:rustc-link-lib=wasi-emulated-signal");
    println!("cargo:rustc-link-lib=wasi-emulated-getpid");
    println!("cargo:rustc-link-lib=wasi-emulated-process-clocks");
    println!("cargo:rustc-link-search=cpython/builddir/wasi/Modules/_decimal/libmpdec");
    println!("cargo:rustc-link-lib=mpdec");
    println!("cargo:rustc-link-search=cpython/builddir/wasi/Modules/expat");
    println!("cargo:rustc-link-lib=expat");
}
