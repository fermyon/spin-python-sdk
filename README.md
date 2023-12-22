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

The bindings are generated from [spin_sdk/wit/spin.wit](./wit/spin.wit).  The
[spin_sdk/wit/deps](./wit/deps) directory was copied from
https://github.com/bytecodealliance/wasmtime/tree/v16.0.0/crates/wasi/wit/deps

```
componentize-py -d spin_sdk/wit -w spin-all bindings bindings
mv bindings/spin_all/* spin_sdk/wit/
rm -r bindings
```
