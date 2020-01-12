# Configuration file for the Sphinx documentation builder.

import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'Cascade-Python'
# pylint:disable=redefined-builtin
copyright = '2020, Bruno Rijsman'
author = 'Bruno Rijsman'
release = '0.0.1'

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
]

templates_path = []
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'

autodoc_default_options = {
    'special-members': '__init__, __repr__, __str__',
}

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def run_apidoc(_):
    modules = ['cascade']
    for module in modules:
        cur_dir = os.path.abspath(os.path.dirname(__file__))
        module = os.path.join(cur_dir, '..', '..', module)
        output_dir = os.path.join(cur_dir, '_modules')
        apidoc = 'sphinx-apidoc'
        if is_venv():
            apidoc = os.path.abspath(os.path.join(sys.prefix, 'bin', 'sphinx-apidoc'))
        exclude_pattern = f"`find {module} -name tests`"
        cmd = f"{apidoc} -f -e -o {output_dir} {module} {exclude_pattern}"
        print(f"**** module={module} output_dir={output_dir} cmd={cmd}")
        subprocess.check_call(cmd, shell=True)

def setup(app):
    app.connect('builder-inited', run_apidoc)
