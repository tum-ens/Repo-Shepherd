# conf.py
# Configuration file for the Sphinx documentation builder.

import os
import sys
# If your project source code is in a specific directory relative to 'docs', add it here.
# For example, if your 'app' folder is one level up from 'docs':
# sys.path.insert(0, os.path.abspath('..'))
# Or if it's alongside 'docs':
sys.path.insert(0, os.path.abspath('../app')) # Adjust if your 'app' location differs
sys.path.insert(0, os.path.abspath('..')) # To find config etc. if needed


# -- Project information -----------------------------------------------------
project = 'Repo Shepherd'
copyright = '2024, TUM'
author = 'TUM'

# The full version, including alpha/beta/rc tags
release = '0.1.0' 


# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',  # Auto-generate docs from docstrings
    'sphinx.ext.napoleon', # Support for Google and NumPy style docstrings
    'sphinx.ext.intersphinx', # Link to other projects' documentation
    'sphinx.ext.viewcode', # Add links to source code
    'sphinx.ext.githubpages', # Helps with GitHub Pages deployment
    # Add any other Sphinx extensions here
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Intersphinx mapping (example)
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


# -- Options for HTML output -------------------------------------------------
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme' # A popular theme, requires 'pip install sphinx-rtd-theme'

html_static_path = []

# Add any custom static files (css, js) here if needed
# html_css_files = [
#     'custom.css',
# ]

# -- Autodoc options ---------------------------------------------------------
autodoc_member_order = 'bysource' # Order members by source code order
# autodoc_default_options = {
#     'members': True,
#     'undoc-members': True,
#     'show-inheritance': True,
# }

# -- Napoleon settings -------------------------------------------------------
# napoleon_google_docstring = True
# napoleon_numpy_docstring = True
# napoleon_include_init_with_doc = False
# napoleon_include_private_with_doc = False
# napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_examples = False
# napoleon_use_admonition_for_notes = False
# napoleon_use_admonition_for_references = False
# napoleon_use_ivar = False
# napoleon_use_param = True
# napoleon_use_rtype = True