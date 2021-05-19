from abc import abstractmethod


class ProxyNotConnectedError(Exception):
    pass


class Proxy():
    """
    Abstract class to represent a generic controller connection proxy
    """

    @abstractmethod
    def connect(self):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    @abstractmethod
    def socket(self):
        raise NotImplementedError()
