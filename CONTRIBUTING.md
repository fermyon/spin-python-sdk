## Building

### Prerequisites

- Python
- `pip`
- `componentize-py` 0.11.2

Once you have `pip` installed, you can install `componentize-py` using:

```bash
pip install componentize-py==0.11.2
```

### Generating the bindings

The bindings are generated from
[src/spin_sdk/wit/spin.wit](./src/spin_sdk/wit/spin.wit).

```bash
componentize-py -d src/spin_sdk/wit -w spin-all bindings bindings --world-module spin_sdk.wit
rm -r src/spin_sdk/wit/imports src/spin_sdk/wit/exports
mv bindings/spin_sdk/wit/* src/spin_sdk/wit/
rm -r bindings
```

### Updating docs

Any time you regenerate the bindings or edit files by hand, you'll want to
regenerate the HTML docs to match.  First, install `pdoc` using `pip install
pdoc3`.  Then, update the docs using:

```bash
./scripts/generate_docs.py
```

### Building the distribution

First, make sure you have an up-to-date version of the `build` package installed:

```bash
pip install --upgrade build
```

Then, build the distribution:

```bash
rm -rf dist
python -m build
```

### Publishing the distribution

First, make sure you have an up-to-date version of the `twine` package installed:

```bash
pip install --upgrade twine
```

Then, publish the distribution:

```bash
twine upload dist/*
```

This first time you run that, it will ask for a username and password.  Enter
`__token__` for the username and specify a valid PyPI token as the password.
Contact Joel Dice for a token if you don't have one.
