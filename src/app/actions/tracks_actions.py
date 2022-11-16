import xbmcgui
import xbmcplugin

from app.actions.base_actions import BaseActions
from app.http import Api
from lib.helpers.logger import Logger


class TracksActions(BaseActions):
    """Holds tracks related actions"""

    @classmethod
    def play(cls, identifiant):
        """
        Get and return the streaming url of the track with the given ID.

        :param identifiant: ID of the track to stream
        :return: track's stream url
        """
        url = Api.instance().request_streaming(identifiant)

        if url.startswith('http'):
            Logger.debug("Playing track " + identifiant)
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(cls.app.args().addon_handle, True, listitem=item)
        else:
            Logger.warn("Unplayable track " + identifiant)
            xbmcgui.Dialog().notification(
                "Unplayable track",
                "Track " + identifiant + " cannot be played.",
                xbmcgui.NOTIFICATION_WARNING,
                sound=False
            )
            xbmcplugin.setResolvedUrl(cls.app.args().addon_handle, False, xbmcgui.ListItem())

        return []
