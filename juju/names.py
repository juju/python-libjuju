import re
from enum import Enum, unique


@unique
class MatchType(Enum):
    MATCH = 1
    SEARCH = 2


MODEL = re.compile('^[a-z0-9]+[a-z0-9-]*$')


def match_model(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(MODEL, val)
    else:
        return re.match(MODEL, val)


APPLICATION = re.compile('^(?:[a-z][a-z0-9]*(?:-[a-z0-9]*[a-z][a-z0-9]*)*)$')


def match_application(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(APPLICATION, val)
    else:
        return re.match(APPLICATION, val)


def is_valid_application(val):
    return match_application(val) is not None


ENDPOINT = re.compile('/?((?P<model>[^\\.]*)\\.)?(?P<appname>[^:]*)(:(?P<endpoints>.*))?')


def match_endpoint(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(ENDPOINT, val)
    else:
        return re.match(ENDPOINT, val)


SOURCE_ENDPOINT = re.compile('^[a-zA-Z0-9]+$')


def match_source_endpoint(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(SOURCE_ENDPOINT, val)
    else:
        return re.match(SOURCE_ENDPOINT, val)


MODEL_APPLICATION = re.compile('(/?((?P<user>[^/]+)/)?(?P<model>[^.]*)(.(?P<application>[^:]*(:.*)?))?)?')


def match_model_application(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(MODEL_APPLICATION, val)
    else:
        return re.match(MODEL_APPLICATION, val)


valid_user_name_snippet = "[a-zA-Z0-9][a-zA-Z0-9.+-]*[a-zA-Z0-9]"
valid_user_snippet = "(?:{}(?:@{})?)".format(valid_user_name_snippet, valid_user_name_snippet)
USER = re.compile("^(?P<name>{})(?:@(?P<domain>{}))?$".format(valid_user_name_snippet, valid_user_name_snippet))


def match_user(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(USER, val)
    else:
        return re.match(USER, val)


RELATION = re.compile("[a-z][a-z0-9]*(?:[_-][a-z0-9]+)*")


def match_relation(val, match_type=None):
    if match_type is MatchType.SEARCH:
        return re.search(RELATION, val)
    else:
        return re.match(RELATION, val)
