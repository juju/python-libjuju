# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import importlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence

import pytest

from juju.client.facade_versions import (
    client_facade_versions,
    excluded_facade_versions,
    known_unsupported_facades,
)


@pytest.fixture
def project_root(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath


@pytest.fixture
def generated_code_facades(project_root: Path) -> Dict[str, Sequence[int]]:
    """Return a {facade_name: (versions,)} dictionary from the generated code.

    Iterates through all the generated files matching
    juju/client/_client*.py, extracting facade types (those that have
    .name and .version properties). Excludes facades in
    juju.client.connection.excluded_facades, as these are manually
    marked as incompatible with the current version of python-libjuju.
    """
    facades: Dict[str, List[int]] = defaultdict(list)
    for file in project_root.glob("juju/client/_client*.py"):
        module = importlib.import_module(f"juju.client.{file.stem}")
        for cls_name in dir(module):
            cls = getattr(module, cls_name)
            try:  # duck typing check for facade types
                assert cls.name
                assert cls.version
            except AttributeError:
                continue
            if cls.version in excluded_facade_versions.get(cls.name, []):
                continue
            facades[cls.name].append(cls.version)
    return {name: tuple(sorted(facades[name])) for name in sorted(facades)}


def test_client_facades(generated_code_facades: Dict[str, Sequence[int]]) -> None:
    """Ensure that juju.client.facade_versions.client_facade_versions matches
    expected facades.

    See generated_code_facades for how expected facades are computed.
    """
    assert client_facade_versions == generated_code_facades


def test_unsupported_facades(generated_code_facades: Dict[str, Sequence[int]]) -> None:
    """Ensure that we don't accidentally ignore our own generated code."""
    assert not set(generated_code_facades) & set(known_unsupported_facades)
