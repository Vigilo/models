NAME := models
EPYDOC_PARSE = vigilo\.models\.(tables|test)
all: build
include buildenv/Makefile.common

install: build install_python install_data
install_pkg: build install_python_pkg install_data

install_python: $(PYTHON)
	$(PYTHON) setup.py install --record=INSTALLED_FILES
install_python_pkg: $(PYTHON)
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR)

install_data: $(wildcard tools/*)
	mkdir -p $(DESTDIR)$(BINDIR)
	install -p -m 755 tools/* $(DESTDIR)$(BINDIR)

lint: lint_pylint
tests: tests_nose
doc: apidoc
clean: clean_python

.PHONY: install_pkg install_python install_python_pkg install_data
