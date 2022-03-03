from .deezerkodi_exception import DeezerKodiException


class ApiException(DeezerKodiException):
    """
    Base exception for every DeezerKodi API exceptions.
    """

    CODE = 0

    def __init__(self, header, message):
        """
        Instantiate a Deezer API error with a header (type) and a message.

        :param header: Header to display
        :param message: Message to display
        """
        DeezerKodiException.__init__(self)
        self.header = header
        self.message = message
