from lib.exceptions import ApiException


class OAuthException(ApiException):
    """This class represents an authentication error"""
    CODE = 200
