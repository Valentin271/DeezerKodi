# -*- coding: utf-8 -*-


class DeezerObject(object):
    """
    Base class for any DeezerAPI class
    """

    def __init__(self, connection, object_content):
        """
        Instantiate a Deezer Object from a `connection` and the `content` of the object.

        :param Connection connection: Connection to the API
        :param dict object_content: Object's content, as returned by the API
        """
        self.connection = connection
        self.__dict__.update(object_content)

    def _update_data(self):
        """
        Update the current object with complete data.\n
        Sometimes the API return incomplete objects.
        """
        data = self.connection.make_request(self.type, self.id)
        self.__dict__.update(data)
