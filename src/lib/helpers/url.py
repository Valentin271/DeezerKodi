"""
Provides helpers functions to manipulate URLs.
"""

from urllib.parse import urlencode


def build(query):
    """
    Build url from `query` dict.
    Used to build url to navigate in kodi menus.

    :param dict query: Options to format
    :return: The encoded url as str
    """
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
