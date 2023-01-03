"""
Provide a wrapper around cli argument given by kodi.
"""

from urllib.parse import parse_qs


class Arguments(object):
    """
    The Arguments class is a wrapper around kodi values retrieved by argv.
    """

    def __init__(self, argv: list):
        """
        Create an Arguments instance.

        :param list argv: argv values given by kodi, 3 first values must be filled
        """
        self.base_url = argv[0]
        self.addon_handle = int(argv[1])
        self.__parameters = Arguments.parse_qs(argv[2][1:])

    @staticmethod
    def parse_qs(qs: str):
        """
        Parse the given HTTP query string into a dict.

        :param str qs: Query string to parse
        :return: A dict
        """
        return parse_qs(qs)

    def get(self, key: str, default=None):
        """
        Get the value of the given key.
        If the result is an array with 1 element (as returned by urllib parse_qs),
        this element is returned.

        :param str key: The key to get
        :param default: The returned value if the key doesn't exist
        :return: The value of the given key, or `default` if it doesn't exist
        """
        value = self.__parameters.get(key, default)

        if isinstance(value, list) and len(value) == 1:
            return value[0]

        return value

    def has(self, key: str):
        """
        Determine if the given key is present in the parameters.

        :param str key: Key to search
        :return: True if the key exist, false otherwise
        """
        return key in self.__parameters

    def set(self, key: str, value):
        """
        Sets the given value to the given key

        :param key: key to set
        :param value: value to set
        """
        self.__parameters[key] = value
