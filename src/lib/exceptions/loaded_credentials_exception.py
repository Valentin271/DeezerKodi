from .deezerkodi_exception import DeezerKodiException


class LoadedCredentialsException(DeezerKodiException):
    """Thrown when credentials loaded from file are faulty (i.e. empty)"""
