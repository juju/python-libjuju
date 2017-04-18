BIN := .tox/py35/bin
PY := $(BIN)/python3.5
PIP := $(BIN)/pip
SCHEMAGEN := $(shell which schemagen)

clean:
	find . -name __pycache__ -type d -exec rm -r {} +
	find . -name *.pyc -delete
	rm -rf .tox

.tox:
	tox -r --notest

client:
ifndef SCHEMAGEN
	$(error "schemagen is not available, please install from https://github.com/juju/schemagen")
endif
	$(PY) -m juju.client.facade -s "juju/client/schemas*" -o juju/client/

test:
	tox

docs: .tox
	$(PIP) install -r docs/requirements.txt
	rm -rf docs/api/* docs/_build/
	$(BIN)/sphinx-apidoc -o docs/api/ juju/
	$(BIN)/sphinx-build -b html docs/  docs/_build/
	cd docs/_build/ && zip -r docs.zip *

upload: docs
	$(PY) setup.py sdist upload upload_docs --upload-dir=docs/_build

.PHONY: clean client test docs upload
