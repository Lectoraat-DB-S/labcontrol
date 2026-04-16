# copied some configuration from https://github.com/pyvisa/pyvisa/blob/main/docs/source/conf.py
import os
import sys
#sys.path.insert(0, os.path.abspath('../../labcontrol/'))
sys.path.insert(0, os.path.abspath('../..'))
sys.path.append(os.path.abspath('../../labcontrol'))
sys.path.append(os.path.abspath('../../labcontrol/devices'))
#sys.path.append(os.path.abspath('..'))
#sys.path.append(os.path.abspath('.'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'labcontrol'
copyright = '2026, eppie'
author = 'eppie'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',]


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
source_suffix = ".rst"
# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("http://docs.python.org/3", None)}
