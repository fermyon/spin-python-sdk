# Experimental [Spin](https://github.com/fermyon/spin) SDK for [componentize-py](https://pypi.org/project/componentize-py/)

This is an experimental SDK for creating Spin apps using `componentize-py`.

## Building

### Prerequisites

- Python
- `pip`
- `componentize-py` 0.8.0

Once you have `pip` installed, you can install `componentize-py` using:

```
pip install componentize-py==0.8.0
```

### Generating the bindings

The bindings are generated from
[src/spin_sdk/wit/spin.wit](./src/spin_sdk/wit/spin.wit).  The
[src/spin_sdk/wit/deps](./src/spin_sdk/wit/deps) directory was copied from
https://github.com/bytecodealliance/wasmtime/tree/v16.0.0/crates/wasi/wit/deps

```
componentize-py -d src/spin_sdk/wit -w spin-all bindings bindings
mv bindings/spin_all/* src/spin_sdk/wit/
rm -r bindings
```
