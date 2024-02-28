# Example: Spin Redis

This is an example showcasing the use of Spin Redis bindings within a guest component. 

## Preparing the Environment

Run the following commands to setup a virtual environment with Python.

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages specified in the `requirements.txt` using the command:

```bash
pip3 install -r requirements.txt
```

For this example, a redis database should be accessable at `localhost:6379`.

## Building and Running the Examples

```bash
spin build --up
```

## Testing the App

```bash
$ curl localhost:3000                      
Hello from Python!
```