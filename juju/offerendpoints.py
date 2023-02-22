#
# Module that parses offer endpoints
#


from .names import (MatchType, match_application, match_endpoint, match_model,
                    match_model_application, match_relation,
                    match_source_endpoint, match_user)


class ParseError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)


class OfferEndpoints:
    def __init__(self, application, endpoints, model=None, qualified_model_name=None):
        self.application = application
        self.endpoints = endpoints
        self.model = model
        self.qualified_model_name = qualified_model_name

    def __eq__(self, other):
        if not isinstance(other, OfferEndpoints):
            return NotImplemented
        return (self.application == other.application and
                self.endpoints == other.endpoints and
                self.model == other.model and
                self.qualified_model_name == other.qualified_model_name)


def parse_offer_endpoint(endpoint):
    if ":" not in endpoint:
        raise ParseError("endpoint must conform to format \"<application-name>:<endpoint-name>\"")

    matches = match_endpoint(endpoint, MatchType.SEARCH)
    if matches is None:
        raise ParseError("endpoint must conform to format \"<application-name>:<endpoint-name>\"")
    model_group = matches.group("model")
    application_group = matches.group("appname")
    endpoints_group = matches.group("endpoints")

    qualified_model_name = None
    if (model_group is not None) and (model_group != ""):
        if ("/" not in model_group):
            raise NotImplementedError()
        qualified_model_name = model_group
        model_group = model_group.split("/")[0]

    if (model_group is not None) and (not match_model(model_group)):
        raise ParseError("model name {}".format(model_group))
    if not match_application(application_group):
        raise ParseError("application name {}".format(application_group))

    model = model_group
    application = application_group

    endpoints = endpoints_group.split(",")
    if len(endpoints) == 0 or len(endpoints_group) == 0:
        raise ParseError("specify endpoints for {}".format(application))

    return OfferEndpoints(application, endpoints, model=model, qualified_model_name=qualified_model_name)


class OfferURL:
    def __init__(self, source="", user="", model="", application=""):
        self.source = source
        self.user = user
        self.model = model
        self.application = application

    def __eq__(self, other):
        if not isinstance(other, OfferURL):
            return NotImplemented
        return (self.source == other.source and
                self.user == other.user and
                self.model == other.model and
                self.application == other.application)

    def has_empty_source(self):
        return self.source is None or self.source == ""

    def has_endpoint(self):
        return ":" in self.application

    def as_local(self):
        return OfferURL("", self.user, self.model, self.application)

    def string(self):
        parts = []
        if self.user != "":
            parts.append(self.user)
        if self.model != "":
            parts.append(self.model)
        path = "/".join(parts)
        path = "{}.{}".format(path, self.application)
        if self.has_empty_source():
            return path
        return "{}:{}".format(self.source, path)


def parse_offer_url(url):
    source, rest = maybe_parse_offer_url_source(url)

    valid = url[0] != ":"
    valid = valid and match_model_application(rest)
    if not valid:
        raise ParseError("application offer URL has invalid form, must be [<user/]<model>.<appname>: {}".format(url))

    offer_source = source

    matches = match_model_application(rest, MatchType.SEARCH)
    offer_user = _get_or_else(matches.group("user"), "")
    offer_model = _get_or_else(matches.group("model"), "")
    offer_application = _get_or_else(matches.group("application"), "")

    if valid and (("/" in offer_model) or ("/" in offer_application)):
        raise ParseError("application offer URL has invalid form, must be [<user/]<model>.<appname>: {}".format(url))
    if not offer_model:
        raise ParseError("application offer URL is missing model")
    if not offer_application:
        raise ParseError("application offer URL is missing application")

    if offer_user and not match_user(offer_user):
        raise ParseError("user name {} not valid".format(offer_user))
    if offer_model and not match_model(offer_model):
        raise ParseError("model name {} not valid".format(offer_model))

    app_name = offer_application.split(":")[0]
    if app_name and not match_application(app_name):
        raise ParseError("application name {} not valid".format(app_name))

    return OfferURL(source=offer_source, user=offer_user, model=offer_model,
                    application=offer_application)


def _get_or_else(val, res):
    if val is None:
        return res
    return val


def maybe_parse_offer_url_source(url):
    parts = url.split(":")
    if len(parts) > 2:
        return parts[0], ":".join(parts[slice(1, len(parts))])
    elif len(parts) == 2:
        if match_source_endpoint(parts[1]):
            return "", url
        return (parts[0], parts[1])
    return "", url


class LocalEndpoint:
    def __init__(self, application="", relation=None):
        self.application = application
        self.relation = relation

    def __eq__(self, other):
        if not isinstance(other, LocalEndpoint):
            return NotImplemented
        return (self.relation == other.relation and
                self.application == other.application)


def parse_local_endpoint(url):
    application_name = url
    relation = None

    if ":" in url:
        if url[0] == ":" or url[-1] == ":":
            raise ParseError("endpoint {} not valid".format(url))

        parts = url.split(":")
        if len(parts) != 2:
            raise ParseError("endpoint {} not valid".format(url))

        application_name = parts[0]

        if not match_relation(parts[1]):
            raise ParseError("endpoint {} not valid".format(url))

        relation = parts[1]

    if not match_application(application_name):
        raise ParseError("endpoint {} not valid".format(application_name))

    return LocalEndpoint(application=application_name, relation=relation)
