fn main() {
    println!("cargo:rustc-link-search=/opt/wasi-sdk/share/wasi-sysroot/lib/wasm32-wasi");
    println!("cargo:rustc-link-lib=wasi-emulated-signal");
    println!("cargo:rustc-link-lib=wasi-emulated-getpid");
    println!("cargo:rustc-link-lib=wasi-emulated-process-clocks");
    println!(
        "cargo:rustc-link-search=/home/dicej/p/cpython/builddir/wasi/Modules/_decimal/libmpdec"
    );
    println!("cargo:rustc-link-lib=mpdec");
    println!("cargo:rustc-link-search=/home/dicej/p/cpython/builddir/wasi/Modules/expat");
    println!("cargo:rustc-link-lib=expat");
}
