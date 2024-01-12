#!/usr/bin/env python3

import os
import shutil

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

wit_module = os.path.join('src', 'spin_sdk', 'wit', '__init__.py')
expected_doc_comment = '""" Module with the bindings generated from the wit by componentize-py """\n\n'

with open(wit_module, 'r') as init_file:
    content = init_file.read()

if expected_doc_comment not in content:
    with open(wit_module, 'w') as init_file:
        init_file.write(expected_doc_comment + content)

# Change to the root directory of the project
os.chdir(os.path.join(script_dir, '..'))

# Remove the 'docs' directory
shutil.rmtree('docs', ignore_errors=True)

# Change directory to 'src' and generate HTML documentation using pdoc
os.chdir('src')
os.system('pdoc --html spin_sdk')

# Move the generated documentation to the 'docs' directory
shutil.move('html/spin_sdk', os.path.join('..', 'docs'))

# Remove the 'src/html' directory
os.rmdir('html')