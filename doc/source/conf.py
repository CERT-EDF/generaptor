import os
import sys
from pathlib import Path
from generaptor.__version__ import version

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

project = 'Generaptor'
copyright = '2025, CERT-EDF'
author = 'CERT-EDF'
release = version
print(version)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

language = 'en'

highlight_language = 'python'

napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_numpy_docstring = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

add_module_names = False

autodoc_class_signature = 'separated'
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': False,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}
autodoc_docstring_signature = True
autodoc_inherit_docstrings = False
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
autodoc_typehints_format = 'short'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_with_keys': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
}
todo_include_todos = True
viewcode_enable = True


def setup(app):
    """Sphinx setup hook"""
    app.add_css_file('custom.css')
