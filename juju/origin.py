# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from enum import Enum

from . import utils
from .errors import JujuError


class Source(Enum):
    """Source defines a origin source. Providing a hint to the controller about
    what the charm identity is from the URL and origin source.

    """

    LOCAL = "local"
    CHARM_HUB = "charm-hub"

    def __str__(self):
        return self.value


class Origin:
    def __init__(self, source, channel, platform):
        self.source = source
        self.channel = channel
        self.platform = platform

    def __str__(self):
        return f"origin using source {self.source!s} for channel {self.channel} and platform {self.platform}"


class Risk(Enum):
    STABLE = "stable"
    CANDIDATE = "candidate"
    BETA = "beta"
    EDGE = "edge"

    def __str__(self):
        return self.value

    @staticmethod
    def valid(potential):
        for risk in [Risk.STABLE, Risk.CANDIDATE, Risk.BETA, Risk.EDGE]:
            if str(risk) == potential:
                return True
        return False


class Channel:
    """Channel identifies and describes completely a store channel.

    A channel consists of, and is subdivided by, tracks, risk-levels and
     - Tracks enable snap developers to publish multiple supported releases of
       their application under the same snap name.
     - Risk-levels represent a progressive potential trade-off between stability
       and new features.

    The complete channel name can be structured as three distinct parts separated
    by slashes:

       <track>/<risk>

    """

    def __init__(self, track=None, risk=None):
        if not Risk.valid(risk):
            raise JujuError(f"unexpected risk {risk}")

        self.track = track or ""
        self.risk = risk

    @staticmethod
    def parse(s: str):
        """Parse a channel from a given string.
        Parse does not take into account branches.

        """
        if not s:
            raise JujuError("channel cannot be empty")

        p = s.split("/")

        risk = None
        track = None
        if len(p) == 1:
            if Risk.valid(p[0]):
                risk = p[0]
            else:
                track = p[0]
                risk = str(Risk.STABLE)
        elif len(p) == 2:
            track = p[0]
            risk = p[1]
        else:
            raise JujuError(f"channel is malformed and has too many components {s}")

        if risk is not None and not Risk.valid(risk):
            raise JujuError(f"risk in channel {s} is not valid")
        if track is not None and track == "":
            raise JujuError(f"track in channel {s} is not valid")

        return Channel(track, risk)

    def normalize(self):
        track = self.track if self.track != "" else ""
        risk = self.risk if self.risk != "" else ""
        return Channel(track, risk)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.track == other.track and self.risk == other.risk
        return False

    def __str__(self):
        path = self.risk
        if self.track != "":
            path = f"{self.track}/{path}"
        return path

    def compute_base_channel(self, series):
        """Determines the channel for a client.Base
        A base channel is a track/risk/branch

        """
        _ch = [self.risk]
        tr = utils.get_series_version(series)
        if tr:
            _ch = [tr, *_ch]
        return "/".join(_ch)


class Platform:
    """ParsePlatform parses a string representing a store platform.
    Serialized version of platform can be expected to conform to the following:

     1. Architecture is mandatory.
     2. OS is optional and can be dropped. Series is mandatory if OS wants
     to be displayed.
     3. Series is also optional.

    To indicate something is missing `unknown` can be used in place.

    Examples:
     1. `<arch>/<os>/<series>`
     2. `<arch>`
     3. `<arch>/<series>`
     4. `<arch>/unknown/<series>`

    """

    def __init__(self, arch, series=None, os=None):
        self.arch = arch
        self.series = series
        self.os = os

    @staticmethod
    def parse(s):
        if not s:
            raise JujuError("platform cannot be empty")

        p = s.split("/")

        arch = None
        os = None
        series = None
        if len(p) == 1:
            arch = p[0]
        elif len(p) == 2:
            arch = p[0]
            series = p[1]
        elif len(p) == 3:
            arch = p[0]
            os = p[1]
            series = p[2]
        else:
            raise JujuError(f"platform is malformed and has too many components {s}")

        if not arch:
            raise JujuError(f"architecture in platform {s} is not valid")
        if os is not None and os == "":
            raise JujuError(f"os in platform {s} is not valid")
        if series is not None and series == "":
            raise JujuError(f"series in platform {s} is not valid")

        return Platform(arch, series, os)

    def normalize(self):
        os = self.os if self.os is not None or self.os != "unknown" else None
        series = self.series
        if series is None or series == "unknown":
            os = None
            series = None

        return Platform(self.arch, series, os)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.arch == other.arch
                and self.os == other.os
                and self.series == other.series
            )
        return False

    def __str__(self):
        path = self.arch
        if self.os is not None and self.os != "":
            path = f"{path}/{self.os}"
        if self.series is not None and self.series != "":
            path = f"{path}/{self.series}"
        return path
