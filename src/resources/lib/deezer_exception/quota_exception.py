"""
This module defines the QuotaException class which represents the Deezer API QUOTA error.
"""

from deezer_exception import DeezerException


class QuotaException(DeezerException):
    """
    Quota error, thrown when too many requests have been sent
    """

    CODE = 4
