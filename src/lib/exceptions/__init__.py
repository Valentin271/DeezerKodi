"""This package contains all custom DeezerKodi exceptions."""

from .api_exception import ApiException
from .credentials_exception import CredentialsException
from .deezerkodi_exception import DeezerKodiException
from .oauth_exception import OAuthException
from .quota_exception import QuotaException


class ApiExceptionFinder:
    """Search the right exception to throw from a given data"""

    __ALL = [
        OAuthException,
        QuotaException
    ]

    @staticmethod
    def from_error(error):
        """
        Search the exception corresponding to the one returned by Deezer API.

        :param dict error: Deezer API error
        """
        for exception in ApiExceptionFinder.__ALL:
            if exception.CODE == error['code']:
                raise exception(error['type'], error['message'])

        raise ApiException(error['type'], error['message'])
