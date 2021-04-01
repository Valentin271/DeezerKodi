# -*- coding: utf-8 -*-

import sys

# Python3
try:
    from urllib.parse import urlencode

# Python2
except ImportError:
    from urllib import urlencode


addon_handle = int(sys.argv[1])

base_url = sys.argv[0]


def build_url(query):
    """
    Build url from `query` dict.
    Used to build url to navigate in menus.

    :param dict query: Options to add in the url
    :return: The encoded url as str
    """
    for k, v in query.items():
        # Python2
        try:
            if isinstance(v, unicode):
                query[k] = v.encode('utf-8')
        # Python3
        except NameError:
            pass

    return base_url + '?' + urlencode(query)
