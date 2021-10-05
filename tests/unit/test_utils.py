import os

from pathlib import Path
from juju.utils import juju_config_dir, juju_ssh_key_paths


def test_config_dir():
    config_dir = juju_config_dir()
    assert os.path.exists(config_dir)
    assert os.path.isdir(config_dir)

    assert os.path.exists(os.path.join(config_dir, 'controllers.yaml'))


def test_juju_ssh_key_paths():
    public, private = juju_ssh_key_paths()
    assert os.path.exists(public)
    assert os.path.isfile(public)

    assert os.path.exists(private)
    assert os.path.isfile(private)

    with Path(public).open('r') as f:
        assert "ssh-rsa" in f.read()

    with Path(private).open('r') as g:
        assert "PRIVATE KEY" in g.read()
