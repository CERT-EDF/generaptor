# Generaptor Documentation

This directory contains the Sphinx documentation for Generaptor.

## Structure

```
doc/
├── Makefile              # Build commands for documentation
├── README.md             # This file
└── source/
    ├── conf.py           # Sphinx configuration
    ├── index.rst         # Main documentation index
    ├── _static/
    │   └── custom.css    # Custom CSS styles
    ...
```

## Prerequisites

- Python 3.12 or higher
- pip
- Sphinx and dependencies (see `../pyproject.toml`)

## Setup

Install the documentation dependencies:

```
python -m pip install -e '.[doc]'
```

## Build Instructions

| Command | Description |
|---------|-------------|
| `make help` | List all available targets |
| `make html` | Build HTML documentation |
| `make html-view` | Build HTML and open in browser |
| `make clean` | Clean build directory |
| `make clean-all` | Clean all Sphinx artifacts |

To build HTML documentation:

```
make html-view
```

The HTML output will be in `doc/build/html/` and `index.html` will be automatically open in your browser.

## Generation from Source

The documentation is automatically generated from:

1. Google docstrings in the source code
2. Hand-written reStructuredText files in `doc/source/`
3. Automatic API documentation from Python modules

All public functions, classes, and methods should use Google docstrings:

    def my_function(param1: str, param2: int) -> bool:
        """Brief description of what the function does.

        Args:
            param1: Description of the first parameter.
            param2: Description of the second parameter.

        Returns:
            Description of the return value.

        Raises:
            ValueError: If something goes wrong.

        Example:
            >>> my_function("hello", 5)
            True
        """

## Customization

The documentation uses the ReadTheDocs theme (`sphinx_rtd_theme`). You can customize it by modifying `html_theme_options` in `conf.py`.

Custom CSS can be added in `doc/source/_static/custom.css`. This file is
automatically loaded by Sphinx.
