#
# Module that parses offer endpoints
#


from .names import (MatchType, match_application, match_endpoint, match_model,
                    match_model_application, match_source_endpoint, match_user)


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

    def string(self):
        parts = []
        if self.user != "":
            parts.append(self.user)
        if self.model != "":
            parts.append(self.model)
        path = "/".join(parts)
        path = "{}.{}".format(path, self.application)
        if self.source == "":
            return path
        return "{}:{}".format(self.source, path)


def parse_offer_url(url):
    result = OfferURL()
    source, rest = maybe_parse_offer_url_source(url)

    valid = url[0] != ":"
    valid = valid and match_model_application(rest)
    if valid:
        result.source = source

        matches = match_model_application(rest, MatchType.SEARCH)
        result.user = _get_or_else(matches.group("user"), "")
        result.model = _get_or_else(matches.group("model"), "")
        result.application = _get_or_else(matches.group("application"), "")
    if not valid or (valid and (("/" in result.model) or ("/" in result.application))):
        raise ParseError("application offer URL has invalid form, must be [<user/]<model>.<appname>: {}".format(url))
    if not result.model:
        raise ParseError("application offer URL is missing model")
    if not result.application:
        raise ParseError("application offer URL is missing application")

    if result.user and not match_user(result.user):
        raise ParseError("user name {} not valid".format(result.user))
    if result.model and not match_model(result.model):
        raise ParseError("model name {} not valid".format(result.model))

    app_name = result.application.split(":")[0]
    if app_name and not match_application(app_name):
        raise ParseError("application name {} not valid".format(app_name))

    return result


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
