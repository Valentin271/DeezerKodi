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
    def log(msg, loglevel):
        """
        Basic log function, adds DeezerKodi prefix.
        """
        xbmc.log('DeezerKodi: {}'.format(msg), loglevel)

    @staticmethod
    def debug(msg):
        """
        Logs a debug information.
        """
        Logger.log(msg, xbmc.LOGDEBUG)

    @staticmethod
    def info(msg):
        """
        Logs an information.
        """
        Logger.log(msg, xbmc.LOGINFO)

    @staticmethod
    def warn(msg):
        """
        Logs a warning.
        """
        Logger.log(msg, xbmc.LOGWARNING)

    @staticmethod
    def error(msg):
        """
        Logs an error.
        """
        Logger.log(msg, xbmc.LOGERROR)

    @staticmethod
    def fatal(msg):
        """
        Logs a fatal error.
        """
        Logger.log(msg, xbmc.LOGFATAL)
