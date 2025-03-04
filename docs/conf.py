# Configuration file for the Sphinx documentation builder.
#
# For the full list of configuration options, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('..'))  # Añade la ruta de tu proyecto (si es necesario)

project = 'Manual para Read the Docs'
copyright = '2023, Jordan Borda'
author = 'Jordan Borda'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon', #google docstring para python
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/mi_logo.png'  # Agrega la ruta a tu logo
html_favicon = '_static/favicon.ico' # Agrega la ruta al favicon (opcional)

html_theme_options = {
    'logo_only': False,  # Cambia a True si solo quieres el logo, sin el nombre del proyecto
    'display_version': False, # Ocultar la versión de la documentación
    'logo': '_static/mi_logo.png' # Opcional: Especifica de nuevo la ruta al logo dentro de las opciones del tema
}

# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True