#
# Module that parses offer endpoints
#

import re

MODEL = re.compile('^[a-z0-9]+[a-z0-9-]*$')
APPLICATION = re.compile('^(?:[a-z][a-z0-9]*(?:-[a-z0-9]*[a-z][a-z0-9]*)*)$')
ENDPOINT = re.compile('/?((?P<model>[^\\.]*)\\.)?(?P<appname>[^:]*)(:(?P<endpoints>.*))?')


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


def parse(endpoint):
    if ":" not in endpoint:
        raise ParseError("endpoints must conform to format \"<application-name>:<endpoint-name>\"")

    matches = re.search(ENDPOINT, endpoint)
    if matches is None:
        raise ParseError("endpoints must conform to format \"<application-name>:<endpoint-name>\"")
    model_group = matches.group("model")
    application_group = matches.group("appname")
    endpoints_group = matches.group("endpoints")

    qualified_model_name = None
    if (model_group is not None) and (model_group != ""):
        if ("/" not in model_group):
            raise NotImplementedError()
        qualified_model_name = model_group
        model_group = model_group.split("/")[0]

    if (model_group is not None) and (not re.match(MODEL, model_group)):
        raise ParseError("model name {}".format(model_group))
    if not re.match(APPLICATION, application_group):
        raise ParseError("application name {}".format(application_group))

    model = model_group
    application = application_group

    endpoints = endpoints_group.split(",")
    if len(endpoints) == 0 or len(endpoints_group) == 0:
        raise ParseError("specify endpoints for {}".format(application))

    return OfferEndpoints(application, endpoints, model=model, qualified_model_name=qualified_model_name)


SOURCE_ENDPOINT = re.compile('^[a-zA-Z0-9]+$')
MODEL_APPLICATION = re.compile('(/?((?P<user>[^/]+)/)?(?P<model>[^.]*)(.(?P<application>[^:]*(:.*)?))?)?')

valid_user_name_snippet = "[a-zA-Z0-9][a-zA-Z0-9.+-]*[a-zA-Z0-9]"
valid_user_snippet = "(?:{}(?:@{})?)".format(valid_user_name_snippet, valid_user_name_snippet)
USER = re.compile("^(?P<name>{})(?:@(?P<domain>{}))?$".format(valid_user_name_snippet, valid_user_name_snippet))


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


def parse_url(url):
    result = OfferURL()
    source, rest = maybe_parse_source(url)

    valid = url[0] != ":"
    valid = valid and re.match(MODEL_APPLICATION, rest)
    if valid:
        result.source = source

        matches = re.search(MODEL_APPLICATION, rest)
        result.user = always(matches.group("user"), "")
        result.model = always(matches.group("model"), "")
        result.application = always(matches.group("application"), "")
    if not valid or (valid and (("/" in result.model) or ("/" in result.application))):
        raise ParseError("application offer URL has invalid form, must be [<user/]<model>.<appname>: {}".format(url))
    if not result.model:
        raise ParseError("application offer URL is missing model")
    if not result.application:
        raise ParseError("application offer URL is missing application")

    if result.user and not re.match(USER, result.user):
        raise ParseError("user name {} not valid".format(result.user))
    if result.model and not re.match(MODEL, result.model):
        raise ParseError("model name {} not valid".format(result.model))

    app_name = result.application.split(":")[0]
    if app_name and not re.match(APPLICATION, app_name):
        return ParseError("application name {} not valid".format(app_name))

    return result


def always(val, res):
    if val is None:
        return res
    return val


def maybe_parse_source(url):
    parts = url.split(":")
    if len(parts) > 2:
        return parts[0], ":".join(parts[slice(1, len(parts))])
    elif len(parts) == 2:
        if re.match(SOURCE_ENDPOINT, parts[1]):
            return "", url
        return (parts[0], parts[1])
    return "", url
