BIN := .tox/py35/bin
PY := $(BIN)/python3.5
PIP := $(BIN)/pip

clean:
	find . -name __pycache__ -type d -exec rm -r {} +
	find . -name *.pyc -delete
	rm -rf .tox

.tox:
	tox -r --notest

client:
	$(PY) -m juju.client.facade -s juju/client/schemas.json -o juju/client/_client.py

test:
	tox

docs: .tox
	$(PIP) list | grep Sphinx || $(PIP) install -U sphinx
	rm -rf docs/api/*
	$(BIN)/sphinx-apidoc -o docs/api/ juju/
	$(BIN)/sphinx-build -b html docs/  docs/_build/

.PHONY: clean client test docs
