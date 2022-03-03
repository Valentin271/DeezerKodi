import xbmcgui

from app.actions.base_actions import BaseActions
from app.http import Api
from app.views.album_view import AlbumView
from app.views.artist_view import ArtistView
from app.views.base_view import BaseView
from app.views.list_view import ListView
from app.views.track_view import TrackView
from lib.helpers.logger import Logger


class SearchActions(BaseActions):
    """Holds search related actions"""

    @classmethod
    def index(cls):
        """
        Returns the search menu
        """
        icons = cls.args.get('path') + '/resources/icons'

        items = [
            BaseView({'path': '/search/tracks'}, 'Search tracks', True)
                .set_icon(icons + '/search.png'),
            BaseView({'path': '/search/albums'}, 'Search albums', True)
                .set_icon(icons + '/search.png'),
            BaseView({'path': '/search/artists'}, 'Search artists', True)
                .set_icon(icons + '/search.png')
        ]

        return items

    @classmethod
    def tracks(cls):
        """
        Shows a search input then searches for tracks.

        :return: ListView of Track or nothing if canceled
        """
        query = xbmcgui.Dialog().input('Search')

        if query == '':
            Logger.debug('Track search canceled')
            return []

        Logger.info('Searching tracks with "{}"'.format(query))
        response = Api.instance().request('search', 'track', parameters={'q': query})

        return ListView(TrackView, response)

    @classmethod
    def albums(cls):
        """
        Shows a search input then searches for albums.

        :return: ListView of Album or nothing if canceled
        """
        query = xbmcgui.Dialog().input('Search')

        if query == '':
            Logger.debug('Album search canceled')
            return []

        Logger.info('Searching albums with "{}"'.format(query))
        response = Api.instance().request('search', 'album', parameters={'q': query})

        return ListView(AlbumView, response)

    @classmethod
    def artists(cls):
        """
        Shows a search input then searches for artists.

        :return: ListView of Artist or nothing if canceled
        """
        query = xbmcgui.Dialog().input('Search')

        if query == '':
            Logger.debug('Artist search canceled')
            return []

        Logger.info('Searching artists with "{}"'.format(query))
        response = Api.instance().request('search', 'artist', parameters={'q': query})

        return ListView(ArtistView, response)
