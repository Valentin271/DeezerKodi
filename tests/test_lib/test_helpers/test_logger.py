import xbmc

from lib.helpers import logger
from mock import Mock
from testcase import TestCase


class TestLogger(TestCase):
    def setUp(self):
        self.__mock = Mock()
        logger.xbmc.log = self.__mock.fn

    def test_debug(self):
        logger.Logger.debug("debug test")

        self.assertCalledOnce(self.__mock)
        self.assertCalledWith(self.__mock, "DeezerKodi: debug test", xbmc.LOGDEBUG)

    def test_info(self):
        logger.Logger.info("info test")

        self.assertCalledOnce(self.__mock)
        self.assertCalledWith(self.__mock, "DeezerKodi: info test", xbmc.LOGINFO)

    def test_warn(self):
        logger.Logger.warn("warning test")

        self.assertCalledOnce(self.__mock)
        self.assertCalledWith(self.__mock, "DeezerKodi: warning test", xbmc.LOGWARNING)

    def test_error(self):
        logger.Logger.error("error test")

        self.assertCalledOnce(self.__mock)
        self.assertCalledWith(self.__mock, "DeezerKodi: error test", xbmc.LOGERROR)

    def test_fatal(self):
        logger.Logger.fatal("fatal test")

        self.assertCalledOnce(self.__mock)
        self.assertCalledWith(self.__mock, "DeezerKodi: fatal test", xbmc.LOGFATAL)
