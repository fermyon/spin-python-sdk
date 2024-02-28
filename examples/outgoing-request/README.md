# Example: Outgoing Request

This is an example showcasing the use of outbound requests within a guest component. 

## Preparing the Environment

Run the following commands to setup a virtual environment with Python.

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages specified in `the requirements.txt` using the command:

```bash
pip3 install -r requirements.txt
```

## Building and Running the Examples

```bash
spin build --up
```

## Testing the App

```bash
$ ccurl -H "url: https://example.com" localhost:3000
<!doctype html>
<html>
<head>
    <title>Example Domain</title>
    ...
```