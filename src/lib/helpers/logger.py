"""
logger module defines helpers functions for loging.
"""

import xbmc


class Logger(object):
    """
    Logger class provides higher level log function for kodi.
    It adds a prefix for DeezerKodi.
    """

    @staticmethod
    def log(msg: str, loglevel: int, *args, **kwargs):
        """
        Basic log function, adds DeezerKodi prefix.
        """
        xbmc.log('DeezerKodi: {}'.format(msg.format(*args, **kwargs)), loglevel)

    @staticmethod
    def debug(msg: str, *args, **kwargs):
        """
        Logs a debug information.
        """
        Logger.log(msg, xbmc.LOGDEBUG, *args, **kwargs)

    @staticmethod
    def info(msg: str, *args, **kwargs):
        """
        Logs an information.
        """
        Logger.log(msg, xbmc.LOGINFO, *args, **kwargs)

    @staticmethod
    def warn(msg: str, *args, **kwargs):
        """
        Logs a warning.
        """
        Logger.log(msg, xbmc.LOGWARNING, *args, **kwargs)

    @staticmethod
    def error(msg: str, *args, **kwargs):
        """
        Logs an error.
        """
        Logger.log(msg, xbmc.LOGERROR, *args, **kwargs)

    @staticmethod
    def fatal(msg: str, *args, **kwargs):
        """
        Logs a fatal error.
        """
        Logger.log(msg, xbmc.LOGFATAL, *args, **kwargs)
