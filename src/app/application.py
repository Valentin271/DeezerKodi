"""
application module defines the App class which represents the DeezerKodi application.
"""
import xbmcaddon
import xbmcgui
import xbmcplugin

from app import routes
from app.http import Router, Api
from app.views.list_view import ListView
from lib.exceptions import ApiException, OAuthException
from lib.exceptions.credentials_exception import CredentialsException
from lib.helpers.logger import Logger


class Application(object):
    """
    Application class.
    Represents a DeezerKodi application instance.
    """

    def __init__(self, args):
        """
        Create an instance of DeezerKodi.

        :param src.app.Arguments args: Arguments given by Kodi
        """
        self.__addon = xbmcaddon.Addon('plugin.audio.deezer')
        Logger.info("Starting DeezerKodi v{}".format(self.__addon.getAddonInfo('version')))

        self.__router = Router(args.get('path', '/'))
        self.__args = args
        self.__args.set('path', self.__addon.getAddonInfo('path'))
        routes.load(self.__router)

    def args(self):
        """
        Arguments getter
        :return: Application's arguments
        """
        return self.__args

    def run(self):
        """
        Run the application. Starts the router and return a list to display by Kodi.

        :return: ListItem list
        """
        items = []

        try:
            items = self.__router.route(self)
        except OAuthException as e:
            xbmcgui.Dialog().notification(e.header, "Refreshing token ...", "", 1000, False)
            Api.clean_cache()
            self.run()
            return
        except CredentialsException:
            self.__addon.openSettings()
            self.run()
            return
        except ApiException as e:
            xbmcgui.Dialog().ok(e.header, e.message)

        if isinstance(items, ListView):
            Logger.debug('Defining content type: {}'.format(items.content_type))
            xbmcplugin.setContent(self.__args.addon_handle, items.content_type)

        for i, item in enumerate(items):
            items[i] = item.view(self.__args.base_url)

        xbmcplugin.addDirectoryItems(self.__args.addon_handle, items, len(items))
        xbmcplugin.endOfDirectory(self.__args.addon_handle)

    def sortable(self, *sorts):
        """
        Enable the given sort methods. Order defines UI order

        :param int sorts: Sort methods to enable
        """
        for sort in sorts:
            xbmcplugin.addSortMethod(self.__args.addon_handle, sort)
