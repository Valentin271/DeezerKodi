from .api_exception import ApiException


class QuotaException(ApiException):
    """Exception occuring when Deezer returns a Quota limit exceeded"""
    CODE = 4
