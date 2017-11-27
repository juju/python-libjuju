from juju.client.overrides import Binary, Number  # noqa

import pytest


# test cases ported from:
# https://github.com/juju/version/blob/master/version_test.go
@pytest.mark.parametrize("input,expected", (
    (None, Number(major=0, minor=0, patch=0, tag='', build=0)),
    (Number(major=1, minor=0, patch=0), Number(major=1, minor=0, patch=0)),
    ({'major': 1, 'minor': 0, 'patch': 0}, Number(major=1, minor=0, patch=0)),
    ("0.0.1", Number(major=0, minor=0, patch=1)),
    ("0.0.2", Number(major=0, minor=0, patch=2)),
    ("0.1.0", Number(major=0, minor=1, patch=0)),
    ("0.2.3", Number(major=0, minor=2, patch=3)),
    ("1.0.0", Number(major=1, minor=0, patch=0)),
    ("10.234.3456", Number(major=10, minor=234, patch=3456)),
    ("10.234.3456.1", Number(major=10, minor=234, patch=3456, build=1)),
    ("10.234.3456.64", Number(major=10, minor=234, patch=3456, build=64)),
    ("10.235.3456", Number(major=10, minor=235, patch=3456)),
    ("1.21-alpha1", Number(major=1, minor=21, patch=1, tag="alpha")),
    ("1.21-alpha1.1", Number(major=1, minor=21, patch=1, tag="alpha",
                             build=1)),
    ("1.21-alpha10", Number(major=1, minor=21, patch=10, tag="alpha")),
    ("1.21.0", Number(major=1, minor=21)),
    ("1234567890.2.1", TypeError),
    ("0.2..1", TypeError),
    ("1.21.alpha1", TypeError),
    ("1.21-alpha", TypeError),
    ("1.21-alpha1beta", TypeError),
    ("1.21-alpha-dev", TypeError),
    ("1.21-alpha_dev3", TypeError),
    ("1.21-alpha123dev3", TypeError),
))
def test_number(input, expected):
    if expected is TypeError:
        with pytest.raises(expected):
            Number.from_json(input)
    else:
        result = Number.from_json(input)
        assert result == expected
        if isinstance(input, str):
            assert result.to_json() == input


# test cases ported from:
# https://github.com/juju/version/blob/master/version_test.go
@pytest.mark.parametrize("input,expected", (
    (None, Binary(Number(), None, None)),
    (Binary(Number(1), 'trusty', 'amd64'), Binary(Number(1),
                                                  'trusty', 'amd64')),
    ({'number': {'major': 1},
      'series': 'trusty',
      'arch': 'amd64'}, Binary(Number(1), 'trusty', 'amd64')),
    ("1.2.3-trusty-amd64", Binary(Number(1, 2, 3, "", 0),
                                  "trusty", "amd64")),
    ("1.2.3.4-trusty-amd64", Binary(Number(1, 2, 3, "", 4),
                                    "trusty", "amd64")),
    ("1.2-alpha3-trusty-amd64", Binary(Number(1, 2, 3, "alpha", 0),
                                       "trusty", "amd64")),
    ("1.2-alpha3.4-trusty-amd64", Binary(Number(1, 2, 3, "alpha", 4),
                                         "trusty", "amd64")),
    ("1.2.3", TypeError),
    ("1.2-beta1", TypeError),
    ("1.2.3--amd64", TypeError),
    ("1.2.3-trusty-", TypeError),
))
def test_binary(input, expected):
    if expected is TypeError:
        with pytest.raises(expected):
            Binary.from_json(input)
    else:
        result = Binary.from_json(input)
        assert result == expected
        if isinstance(input, str):
            assert result.to_json() == input
