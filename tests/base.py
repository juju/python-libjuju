import subprocess

import pytest


def is_bootstrapped():
    result = subprocess.run(['juju', 'switch'], stdout=subprocess.PIPE)
    return (
        result.returncode == 0 and
        len(result.stdout.decode().strip()) > 0)

bootstrapped = pytest.mark.skipif(
    not is_bootstrapped(),
    reason='bootstrapped Juju environment required')
