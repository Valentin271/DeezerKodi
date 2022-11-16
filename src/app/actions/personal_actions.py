from app.actions.base_actions import BaseActions
from app.http import Api
from app.views.album_view import AlbumView
from app.views.artist_view import ArtistView
from app.views.base_view import BaseView
from app.views.list_view import ListView
from app.views.playlist_view import PlaylistView
from app.views.track_view import TrackView


class PersonalActions(BaseActions):
    """Holds actions for a personal account"""

    @classmethod
    def index(cls):
        """Displays the menu for a personal account (or main profile for family account)."""
        icons = cls.app.args().get('path') + '/resources/icons'

        return [
            BaseView({'path': '/personal/playlists'}, 'Playlists', True)
            .set_icon(icons + '/playlists.png'),
            BaseView({'path': '/personal/albums'}, 'Albums', True)
            .set_icon(icons + '/albums.png'),
            BaseView({'path': '/personal/artists'}, 'Artists', True)
            .set_icon(icons + '/artists.png'),
            BaseView({'path': '/personal/flow'}, 'Flow', True)
        ]

    @classmethod
    def playlists(cls):
        """Get the playlists of this user"""
        response = Api.instance().request('user', 'me', 'playlists')
        return ListView(PlaylistView, response)

    @classmethod
    def albums(cls):
        """Get the albums of this user"""
        response = Api.instance().request('user', 'me', 'albums')
        return ListView(AlbumView, response)

    @classmethod
    def artists(cls):
        """Get the artists of this user"""
        response = Api.instance().request('user', 'me', 'artists')
        return ListView(ArtistView, response)

    @classmethod
    def flow(cls):
        """Get the flow tracks of this user"""
        response = Api.instance().request('user', 'me', 'flow')
        return ListView(TrackView, response)
