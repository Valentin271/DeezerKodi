import xbmcplugin

from app.actions.base_actions import BaseActions
from app.http import Api
from app.views.list_view import ListView
from app.views.track_view import TrackView


class PlaylistsActions(BaseActions):
    """Holds playlists related actions"""

    @classmethod
    def show(cls, identifiant):
        """
        Display a playlist content

        :param identifiant: playlist's ID
        :return: playlist's content
        """
        # using playlist/id instead of playlist/id/tracks
        # because data is significantly lighter
        # and we don't need all the artist info (only the name)
        response = Api.instance().request('playlist', identifiant)

        cls.app.sortable(
            xbmcplugin.SORT_METHOD_UNSORTED,
            xbmcplugin.SORT_METHOD_DATE,
            xbmcplugin.SORT_METHOD_TITLE,
            xbmcplugin.SORT_METHOD_ALBUM,
            xbmcplugin.SORT_METHOD_ARTIST,
        )

        return ListView(TrackView, response['tracks'])
