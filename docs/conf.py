import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "loopiase"
author = "DigitalTolk"
release = "0.0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = []
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_static_path = []

autodoc_member_order = "bysource"
autodoc_typehints = "description"
