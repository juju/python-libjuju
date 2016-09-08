PY := .tox/py35/bin/python3.5

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

.phony: clean client test
