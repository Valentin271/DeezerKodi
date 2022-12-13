"""This package contains all custom DeezerKodi exceptions."""

from .api_exception import ApiException
from .credentials_exception import CredentialsException
from .deezerkodi_exception import DeezerKodiException
from .oauth_exception import OAuthException
from .quota_exception import QuotaException


class ApiExceptionFinder:
    """Search the right exception to throw from a given data"""

    __ALL = [
        ApiException,
        OAuthException,
        QuotaException
    ]

    @staticmethod
    def from_error(error):
        """
        Search the exception corresponding to the one returned by Deezer API.
        If no exception is found, base ApiException is raised.
        If error contains no message, the whole error is put in the message.

        :param dict error: Deezer API error
        """
        for exception in ApiExceptionFinder.__ALL:
            if exception.CODE == error.get('code', 0):
                raise exception(error.get('type', 'API Error'), error.get('message', str(error)))

        raise ApiException(error.get('type', 'API Error'), error.get('message', str(error)))
