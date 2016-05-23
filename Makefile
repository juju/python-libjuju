PY := .tox/py35/bin/python3.5

.tox:
	tox -r --notest

.phony: client
client:
	$(PY) -m juju.client.facade -s juju/client/schemas.json -o juju/client/client.py

.phony: test
test:
	tox
