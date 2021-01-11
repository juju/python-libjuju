from enum import Enum
from .errors import JujuError
from urllib.parse import urlparse


class Schema(Enum):
    LOCAL = "local"
    CHARM_STORE = "cs"
    CHARM_HUB = "ch"

    def matches(self, potential):
        return self.value == potential

    def __str__(self):
        return self.value


class URL:
    def __init__(self, schema, user=None, name=None, revision=None, series=None):
        self.schema = schema
        self.user = user
        self.name = name
        self.series = series

        # 0 can be a valid revision, hence the more verbose check.
        if revision is None:
            revision = -1
        self.revision = revision

    @staticmethod
    def parse(s):
        """parse parses the provided charm URL string into its respective
            structure.

            A missing schema is assumed to be 'ch'.

        """
        u = urlparse(s)
        if u.query != "" or u.fragment != "" or u.username or u.password:
            raise JujuError("charm or bundle URL {} has unrecognized parts".format(u))

        if Schema.LOCAL.matches(u.scheme):
            c = parse_v1_url(Schema.LOCAL, u, s)
        elif Schema.CHARM_STORE.matches(u.scheme):
            c = parse_v1_url(Schema.CHARM_STORE, u, s)
        else:
            c = parse_v2_url(u, s)

        if not c.schema:
            raise JujuError("expected schema for charm or bundle URL {}".format(u))
        return c

    def with_revision(self, rev):
        return URL(self.schema, self.user, self.name, rev, self.series)

    def path(self):
        parts = []
        if self.user:
            parts.append("~{}".format(self.user))
        if self.series:
            parts.append(self.series)
        if self.revision is not None and self.revision >= 0:
            parts.append("{}-{}", self.name, self.revision)
        else:
            parts.append(self.name)
        return "/".join(parts)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.schema == other.schema and \
                self.user == other.user and \
                self.name == other.name and \
                self.revision == other.revision and \
                self.series == other.series
        return False

    def __str__(self):
        return "{}:{}".format(str(self.schema), self.path())


def parse_v1_url(schema, u, s):
    c = URL(schema)

    parts = u.path.split("/")
    if len(parts) < 1 or len(parts) > 4:
        raise JujuError("charm or bundle URL has invalid form {}".format(s))

    # ~<username>
    if parts[0].startswith("~"):
        if schema == Schema.LOCAL:
            raise JujuError("local charm or bundle URL with username {}".format(s))
        c.user = parts[0][1:]
        parts = parts[1:]

    if len(parts) > 2:
        raise JujuError("charm or bundle URL has invalid form {}".format(s))

    # <series>
    if len(parts) == 2:
        c.series = parts[0]
        parts = parts[1:]
        # TODO (stickupkid) - validate the series.

    if len(parts) < 1:
        raise JujuError("URL without charm or bundle name {}".format(s))

    (c.name, c.revision) = extract_revision(parts[0])
    # TODO (stickupkid) - validate the name.

    return c


def parse_v2_url(u, s):
    c = URL(Schema.CHARM_HUB)

    parts = u.path.split("/")
    if len(parts) != 1:
        raise JujuError("charm or bundle URL {} malformed, expected <name>".format(s))

    (c.name, c.revision) = extract_revision(parts[0])
    # TODO (stickupkid) - validate the name.

    return c


def extract_revision(name):
    revision = -1
    for i in range(len(name) - 1, -1, -1):
        c = name[i]
        if c.isnumeric():
            continue
        if c == "-" and i != (len(name) - 1):
            revision = int(name[(i + 1):])
            name = name[:i]
        break
    return (name, revision)
