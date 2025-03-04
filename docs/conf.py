# Configuration file for the Sphinx documentation builder.

import os
import sys

#sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'Manual para Read the Docs'
copyright = '2023, Jordan Borda'
author = 'Jordan Borda'
release = '0.1'
version = '0.1'

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinx-prompt",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
]

templates_path = ['_templates']  # Si tienes plantillas personalizadas
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Ruta al logo (asegúrate de que sea correcta)
html_logo = '_static/mi_logo.png'  # <---- ¡VERIFICAR ESTA RUTA!
html_favicon = '_static/favicon.ico' # Agregar Favicon

html_theme_options = {
    "logo_only": False, # Cambiar a True si solo quieres el logo
    "display_version": False, # Ocultar la versión
    "logo": '_static/mi_logo.png' #Especificar logo
}

html_context = {
    "conf_py_path": "/docs/",  # Ajusta si es necesario
    "display_github": True,
    "github_user": "jordanborda", # Tu nombre de usuario de GitHub
    "github_repo": "SGD_V5",    # Nombre de tu repositorio
    "github_version": "main",  # Rama
}