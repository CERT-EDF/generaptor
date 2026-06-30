# Makefile for Sphinx documentation
#
# Usage:
#   make html      # Build HTML documentation
#   make clean     # Clean build directory
#   make help      # Show all available targets

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Internal variables.
PAPER      ?=
BUILDDIRPOSIX := $(shell echo $(BUILDDIR) | sed 's,:,/,g')

# Usage
help:
	@echo "Available targets:"
	@echo "  help           - Show Sphinx help"
	@echo "  html           - Build HTML documentation"
	@echo "  html-view      - Build HTML and open in browser"
	@echo "  clean          - Clean build directory"
	@echo "  clean-all      - Clean all Sphinx artifacts"
	@echo ""
	@echo "Usage: make <target>"


.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the old
# make batch command.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Build HTML documentation
html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "HTML documentation built in $(BUILDDIR)/html"

# Build HTML and open in browser
html-view:
	@$(MAKE) html
	@python -m webbrowser "$(BUILDDIR)/html/index.html" || echo "Opening browser failed. Please open $(BUILDDIR)/html/index.html manually."

# Clean build directory
clean:
	@echo "Cleaning build directory..."
	rm -rf "$(BUILDDIR)"
	@echo "Build directory cleaned"

# Clean all Sphinx artifacts
clean-all: clean
	rm -rf "$(SOURCEDIR)/*.doctree" "$(SOURCEDIR)/_build"
	rm -rf "$(SOURCEDIR)/_static/_build"
	rm -rf "$(SOURCEDIR)/.doctrees"
