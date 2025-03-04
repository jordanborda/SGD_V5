# conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'Nombre de tu proyecto'
author = 'Tu nombre'
release = '0.1'

extensions = [
    'sphinx.ext.autodoc',   # Si deseas documentar código Python
    'sphinx.ext.napoleon',  # Para admitir docstrings en formato Google o NumPy
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']
