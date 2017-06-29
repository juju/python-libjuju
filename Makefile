BIN := .tox/py35/bin
PY := $(BIN)/python3.5
PIP := $(BIN)/pip
SCHEMAGEN := $(shell which schemagen)
VERSION=$(shell cat VERSION)

clean:
	find . -name __pycache__ -type d -exec rm -r {} +
	find . -name *.pyc -delete
	rm -rf .tox
	rm -rf docs/_build/

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
	rm -rf docs/_build/
	$(BIN)/sphinx-build -b html docs/  docs/_build/
	cd docs/_build/ && zip -r docs.zip *

release:
	git remote | xargs -L1 git fetch --tags
	$(PY) setup.py sdist upload
	git tag ${VERSION}
	git remote | xargs -L1 git push --tags

upload: release


.PHONY: clean client test docs upload release
