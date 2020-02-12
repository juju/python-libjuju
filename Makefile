BIN := .tox/py3/bin
PY := $(BIN)/python
PIP := $(BIN)/pip
VERSION=$(shell cat VERSION)

.PHONY: clean
clean:
	find . -name __pycache__ -type d -exec rm -r {} +
	find . -name *.pyc -delete
	rm -rf .tox
	rm -rf docs/_build/

.PHONY: .tox
.tox:
	tox -r --notest

.PHONY: client
client: .tox
	$(PY) -m juju.client.facade -s "juju/client/schemas*" -o juju/client/

.PHONY: test
test:
	tox

.PHONY: lint
lint: 
	tox -e lint --notest

.PHONY: docs
docs: .tox
	$(PIP) install -r docs/requirements.txt
	rm -rf docs/_build/
	$(BIN)/sphinx-build -b html docs/  docs/_build/
	cd docs/_build/ && zip -r docs.zip *

.PHONY: release
release:
	git fetch --tags
	rm dist/*.tar.gz || true
	$(PY) setup.py sdist
	$(BIN)/twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
	git tag ${VERSION}
	git push --tags

.PHONY: upload
upload: release

.PHONY: install-deb-build-deps
install-deb-build-deps:
	sudo apt install -y python3-all debhelper sbuild schroot ubuntu-dev-tools
	$(PIP) install stdeb

.PHONY: build-deb
build-deb: install-deb-build-deps
	rm -rf deb_dist
	$(PY) setup.py --command-packages=stdeb.command bdist_deb
