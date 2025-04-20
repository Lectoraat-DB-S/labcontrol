import sys
import os
sys.path.insert(0, os.path.abspath('../../src/'))
sys.path.append(os.path.abspath('../..'))
sys.path.append(os.path.abspath('..'))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'labcontrol'
copyright = '2025, E. Snijder'
author = 'E. Snijder'
release = '2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',]

templates_path = ['_templates']
exclude_patterns = ['prettyScope']
#autodoc_mock_imports = ['src']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
