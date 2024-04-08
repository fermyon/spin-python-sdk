# Spin Python SDK

This is an SDK for creating [Spin](https://github.com/fermyon/spin) apps using Python.

Note that this SDK supersedes an earlier, experimental version, which may be
found in the [old-sdk](https://github.com/fermyon/spin-python-sdk/tree/old-sdk)
branch.

## [API Documentation](https://fermyon.github.io/spin-python-sdk/v3/index.html)

## Example

### Prerequisites

- [Python 3.10 or later and pip](https://www.python.org/downloads/)
- [componentize-py](https://pypi.org/project/componentize-py/)
- [spin-sdk](https://pypi.org/project/spin-sdk/)
- [Spin](https://github.com/fermyon/spin) 2.2 or later.
- [MyPy](https://pypi.org/project/mypy/) -- This is optional, but useful for during development.

Once you have Python and pip installed, you can use the latter to create and
enter a virtual environment and then install the desired packages

```shell
python -m venv .venv
source .venv/bin/activate
pip install componentize-py==0.13.2 spin-sdk==3.0.0 mypy==1.8.0
```

### Hello, World

A minimal app requires two files: a `spin.toml` and a Python script, which we'll
name `app.py`:

```shell
cat >spin.toml <<EOF
spin_manifest_version = 2

[application]
name = "hello"
version = "0.1.0"
authors = ["Dev Eloper <dev@example.com>"]

[[trigger.http]]
route = "/..."
component = "hello"

[component.hello]
source = "app.wasm"
[component.hello.build]
command = "componentize-py -w spin-http componentize app -o app.wasm"
EOF
```

```shell
cat >app.py <<EOF
from spin_sdk import http
from spin_sdk.http import Request, Response

class IncomingHandler(http.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
EOF
```

Once you've created those files, you can check, build, and run your app:

```.py
python -m mypy app.py
spin build -u
```

Finally, you can test your app using e.g. `curl` in another terminal:

```shell
curl -i http://127.0.0.1:3000
```

If all goes well, you should see:

```
HTTP/1.1 200 OK
content-type: text/plain
transfer-encoding: chunked
date: Tue, 09 Jan 2024 18:26:52 GMT

Hello from Python!
```

Please file an issue if you have any trouble.

See the [examples directory](https://github.com/fermyon/spin-python-sdk/tree/main/examples) in the repository for more examples.
