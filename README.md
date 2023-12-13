# Experimental [Spin](https://github.com/fermyon/spin) SDK for [componentize-py](https://pypi.org/project/componentize-py/)

This is an experimental SDK for creating Spin apps using `componentize-py`.

## Building

### Prerequisites

- Python
- `pip`
- `componentize-py` 0.7.1

Once you have `pip` installed, you can install `componentize-py` using:

```
pip install componentize-py==0.7.1
```

### Generating the bindings

The bindings are generated from [wit/spin.wit](./wit/spin.wit).  The
[wit/deps](./wit/deps) directory was copied from
https://github.com/bytecodealliance/wasmtime/tree/v15.0.1/crates/wasi/wit/deps

```
componentize-py -d wit -w spin bindings bindings
```

That will create a new `bindings` directory containing the bindings.
