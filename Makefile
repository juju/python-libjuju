BIN := .tox/py3/bin
PY := $(BIN)/python3
PIP := $(BIN)/pip3
VERSION := $(shell $(PY) -c "from juju.version import CLIENT_VERSION; print(CLIENT_VERSION)")

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
client:
	tox -r --notest -e lint,py3
	$(PY) -m juju.client.facade -s "juju/client/schemas*" -o juju/client/

.PHONY: run-unit-tests
run-unit-tests: lint .tox
	tox -e py3

.PHONY: run-integration-tests
run-integration-tests: lint .tox
	tox -e integration

.PHONY: run-all-tests
test: run-unit-tests run-integration-tests

.PHONY: lint
lint:
	@./scripts/copyright.sh
	@echo "==> Running flake8 linter"
	tox -e lint

.PHONY: docs
docs:
	tox -e docs

.PHONY: build-test
build-test:
	rm -rf venv
	python -m venv venv
	. venv/bin/activate
	$(PY) setup.py sdist
	pip install dist/juju-${VERSION}.tar.gz
	python3 -c "from juju.controller import Controller"
	rm dist/juju-${VERSION}.tar.gz

.PHONY: release
release:
	git fetch --tags
	rm dist/*.tar.gz || true
	$(PY) setup.py sdist
	$(BIN)/twine check dist/*
	$(BIN)/twine upload --repository juju dist/*
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
