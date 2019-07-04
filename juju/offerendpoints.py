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
        return self.application == other.application and \
               self.endpoints == other.endpoints and \
               self.model == other.model and \
               self.qualified_model_name == other.qualified_model_name


def parse(endpoint):
    if ":" not in endpoint:
        raise ParseError("endpoints must conform to format \"<application-name>:<endpoint-name>\"")

    matches = re.search(ENDPOINT, endpoint)
    model_group = matches.group("model")
    application_group = matches.group("appname")
    endpoints_group = matches.group("endpoints")

    qualified_model_name = None
    if (model_group is not None) and (model_group is not ""):
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
