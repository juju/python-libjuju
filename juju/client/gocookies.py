import datetime
import http.cookiejar as cookiejar
import json
import time

import pyrfc3339


class GoCookieJar(cookiejar.FileCookieJar):
    '''A CookieJar implementation that reads and writes cookies
    to the cookiejar format as understood by the Go package
    github.com/juju/persistent-cookiejar.'''
    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        '''Implement the _really_load method called by FileCookieJar
        to implement the actual cookie loading'''
        data = json.load(f) or []
        now = time.time()
        for cookie in map(go_to_py_cookie, data):
            if not ignore_expires and cookie.is_expired(now):
                continue
            self.set_cookie(cookie)

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        '''Implement the FileCookieJar abstract method.'''
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(cookiejar.MISSING_FILENAME_TEXT)

        # TODO: obtain file lock, read contents of file, and merge with
        # current content.
        go_cookies = []
        now = time.time()
        for cookie in self:
            if not ignore_discard and cookie.discard:
                continue
            if not ignore_expires and cookie.is_expired(now):
                continue
            go_cookies.append(py_to_go_cookie(cookie))
        with open(filename, "w") as f:
            f.write(json.dumps(go_cookies))


def go_to_py_cookie(go_cookie):
    '''Convert a Go-style JSON-unmarshaled cookie into a Python cookie'''
    expires = None
    if go_cookie.get('Expires') is not None:
        t = pyrfc3339.parse(go_cookie['Expires'])
        expires = t.timestamp()
    return cookiejar.Cookie(
        version=0,
        name=go_cookie['Name'],
        value=go_cookie['Value'],
        port=None,
        port_specified=False,
        # Unfortunately Python cookies don't record the original
        # host that the cookie came from, so we'll just use Domain
        # for that purpose, and record that the domain was specified,
        # even though it probably was not. This means that
        # we won't correctly record the CanonicalHost entry
        # when writing the cookie file after reading it.
        domain=go_cookie['Domain'],
        domain_specified=not go_cookie['HostOnly'],
        domain_initial_dot=False,
        path=go_cookie['Path'],
        path_specified=True,
        secure=go_cookie['Secure'],
        expires=expires,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None,
        rfc2109=False,
    )


def py_to_go_cookie(py_cookie):
    '''Convert a python cookie to the JSON-marshalable Go-style cookie form.'''
    # TODO (perhaps):
    #   HttpOnly
    #   Creation
    #   LastAccess
    #   Updated
    # not done properly: CanonicalHost.
    go_cookie = {
        'Name': py_cookie.name,
        'Value': py_cookie.value,
        'Domain': py_cookie.domain,
        'HostOnly': not py_cookie.domain_specified,
        'Persistent': not py_cookie.discard,
        'Secure': py_cookie.secure,
        'CanonicalHost': py_cookie.domain,
    }
    if py_cookie.path_specified:
        go_cookie['Path'] = py_cookie.path
    if py_cookie.expires is not None:
        unix_time = datetime.datetime.fromtimestamp(py_cookie.expires)
        # Note: fromtimestamp bizarrely produces a time without
        # a time zone, so we need to use accept_naive.
        go_cookie['Expires'] = pyrfc3339.generate(unix_time, accept_naive=True)
    return go_cookie
