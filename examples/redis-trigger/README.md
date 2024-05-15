# Example: External Library

This is an example showcasing the use of an external library [`http-router`](https://pypi.org/project/http-router/) within a guest component. 

## Preparing the Environment

Run the following commands to setup a virtual environment with Python.

```bash
python3 -m venv venv
source venv/bin/activate
```

This app also needs a [redis server](https://redis.io/) running on the port `6379`. Installation information can be found [here](https://redis.io/docs/install/). Once installed the server can be started using:

```bash
redis-server
```

Install the required packages specified in the `requirements.txt` using the command:

```bash
pip3 install -r requirements.txt
```

## Building and Running the Examples

```bash
spin build --up
```

## Testing the App

Send a message on a redis channel named `messages`:

```bash
$ redis-cli
127.0.0.1:6379> publish messages "hello world"
```

The app should output:

```bash
hello world
```
