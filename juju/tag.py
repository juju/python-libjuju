# TODO: Tags should be a proper class, so that we can distinguish whether
# something is already a tag or not.  For example, 'user-foo' is a valid
# username, but is ambiguous with the already-tagged username 'foo'.


def _prefix(prefix, s):
    if s and not s.startswith(prefix):
        return '{}{}'.format(prefix, s)
    return s


def untag(prefix, s):
    if s and s.startswith(prefix):
        return s[len(prefix):]
    return s


def cloud(cloud_name):
    return _prefix('cloud-', cloud_name)


def credential(cloud, user, credential_name):
    credential_string = '{}_{}_{}'.format(cloud, user, credential_name)
    return _prefix('cloudcred-', credential_string)


def model(cloud_name):
    return _prefix('model-', cloud_name)


def user(username):
    return _prefix('user-', username)


def application(app_name):
    return _prefix('application-', app_name)


def action(action_uuid):
    return _prefix('action-', action_uuid)
