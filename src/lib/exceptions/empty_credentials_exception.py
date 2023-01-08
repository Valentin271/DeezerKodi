from .deezerkodi_exception import DeezerKodiException


class EmptyCredentialsException(DeezerKodiException):
    """Exception thrown when user credentials are not present"""
