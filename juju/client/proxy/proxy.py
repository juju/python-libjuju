# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from abc import abstractmethod

from juju.errors import AbstractMethodError


class ProxyNotConnectedError(Exception):
    pass


class Proxy():
    """
    Abstract class to represent a generic controller connection proxy
    """

    @abstractmethod
    def connect(self):
        raise AbstractMethodError()

    @abstractmethod
    def close(self):
        raise AbstractMethodError()

    @abstractmethod
    def socket(self):
        raise AbstractMethodError()
