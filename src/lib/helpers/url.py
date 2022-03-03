"""
Provides helpers functions to manipulate URLs.
"""

# Python3
try:
    from urllib.parse import urlencode
# Python2
except ImportError:
    # pylint: disable=no-name-in-module
    from urllib import urlencode


def build(query):
    """
    Build url from `query` dict.
    Used to build url to navigate in kodi menus.

    :param dict query: Options to format
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

    return urlencode(query)


def concat(*items):
    """
    Concatenates multiple elements together to form an url.

    :param str|int items: Path elements
    :return: A path containing all the elements
    """
    path = '/'
    path += '/'.join((str(x).strip('/') for x in items))

    return path
