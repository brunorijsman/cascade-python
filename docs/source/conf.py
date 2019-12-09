# Configuration file for the Sphinx documentation builder.

import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'BB84'
# pylint:disable=redefined-builtin
copyright = '2019, Bruno Rijsman'
author = 'Bruno Rijsman'
release = '0.0.1'

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.apidoc',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def run_apidoc(_):
    modules = ['bb84']
    for module in modules:
        cur_dir = os.path.abspath(os.path.dirname(__file__))
        print(f"cur_dir = {cur_dir}")
        output_path = os.path.join(cur_dir, '_modules')
        print(f"output_path = {output_path}")
        cmd_path = 'sphinx-apidoc'
        exclude_pattern = f"`find {module} -name tests`"
        if is_venv():
            cmd_path = os.path.abspath(os.path.join(sys.prefix, 'bin', 'sphinx-apidoc'))
        print([cmd_path, '-f', '-e', '-o', output_path, module, exclude_pattern])
        cmd = f"{cmd_path} -f -e -o {output_path} {module} {exclude_pattern}"
        subprocess.check_call(cmd, shell=True)


        # subprocess.check_call([cmd_path, '-f', '-e', '-o', output_path, module, exclude_pattern],
        #                       shell=True)

def setup(app):
    app.connect('builder-inited', run_apidoc)
