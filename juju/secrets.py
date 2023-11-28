# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This module contains utility logic for secrets such as reading secret data from yaml and creating data bag for secrets.
"""


import base64
import json
import re
import yaml
from pathlib import Path
from . import errors

file_suffix = "#file"
max_value_size_bytes = 5 * 1024
max_content_size_bytes = 64 * 1024


def create_secret_data(args):
    """CreateSecretData creates a secret data bag from a list of arguments.
    If a key has the #base64 suffix, then the value is already base64 encoded,otherwise the value is base64 encoded as it is added to the data bag.

    If a key has the '#file' suffix, the value is read from the corresponding file.

    :return []str: bag of key value pairs for a secret
    """
    data = {}
    for val in args:
        # Remove any base64 padding ("=") before splitting the key=value.
        stripped = val.rstrip(base64.b64encode(b'=').decode('utf-8'))
        idx = stripped.find("=")
        if idx < 1:
            raise ValueError(f"Invalid key value {val}")

        key = stripped[0:idx]
        value = stripped[idx + 1:]

        # If the key doesn't have the #file suffix, then add it to the bag and continue.
        if not key.endswith(file_suffix):
            data[key] = value
            continue

        key = key.rstrip(file_suffix)
        path = Path(value).resolve()
        try:
            fs = path.stat()
            if fs.st_size > max_value_size_bytes:
                raise ValueError(f"Secret content in file {path} too large: {fs.st_size} bytes")
            content = path.read_text()
            data[key] = content
        except Exception as e:
            raise ValueError(f"Error processing key {key}: {e}")

    return encode_values_base64(data)


def read_secret_data(file):
    """ReadSecretData reads secret data from a YAML or JSON file as key value pairs.

    :param file str: Path to a YAML or JSON file to read values from.

    :return []str: bag of key value pairs for a secret
    """
    data = {}
    path = Path(file).resolve()

    try:
        fs = path.stat()
        if fs.st_size > max_content_size_bytes:
            raise ValueError(f"Secret content in file {path} too large: {fs.st_size} bytes")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {path} does not exist.")
    except OSError:
        raise

    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = file.read()
    except Exception:
        raise

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        try:
            data = yaml.safe_load(data)
        except yaml.YAMLError:
            raise errors.JujuNotValid(f"Invalid data file at: {file}")

    return encode_values_base64(data)


base64_suffix = "#base64"
key_reg_exp = re.compile("^([a-z](?:-?[a-z0-9]){2,})$")


def encode_values_base64(data):
    """Encodes the values in the given data bag for a secret

    If a key has the #base64 suffix, then the value is already base64 encoded,otherwise the value is base64 encoded as it is added to the data bag.
    """

    out = {}
    content_size = 0
    for k, v in data.items():
        if len(v) > max_value_size_bytes:
            raise ValueError(f"secret content for key {k} too large: {len(v)} bytes")
        content_size += len(v)
        if k.endswith(base64_suffix):
            k = k[:-7]
            if not key_reg_exp.match(k):
                raise ValueError(f"Not valid key: {k}")
            out[k] = v
            continue
        if not key_reg_exp.match(k):
            raise ValueError(f"Not valid key: {k}")
        out[k] = base64.b64encode(str(v).encode()).decode()
    if content_size > max_content_size_bytes:
        raise ValueError(f"secret content too large: {content_size} bytes")
    return out
