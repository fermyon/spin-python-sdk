## Updating docs

Any time you edit files under the `spin_sdk` directory, you'll want to
regenerate the HTML docs to match.  First, install `pdoc` using `pip install
pdoc3`.  Then, update the docs using:

```
rm -r docs
pdoc --html spin_sdk
mv html/spin_sdk docs
rmdir html
```
