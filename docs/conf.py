# Configuration file for the Sphinx documentation builder.
#
# For the full list of configuration options, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))  # Añade la ruta de tu proyecto (si es necesario)

# -- Project information -----------------------------------------------------
project = 'Manual para Sistema de Gestion Documentaria V5'
copyright = '2025, Jordan Borda'
author = 'Jordan Borda'
release = '0.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Para soportar Google style docstrings en Python
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'es'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Actualiza para usar las mismas imágenes e íconos que la documentación de Read the Docs
html_logo = 'img/logo.svg'
html_favicon = 'img/favicon.ico'

html_theme_options = {
    'logo_only': True,       # Muestra solo el logo, sin el nombre del proyecto
    'display_version': False,  # Oculta la versión de la documentación
}

# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True
