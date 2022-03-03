from .base_actions import BaseActions
from ..http import Api
from ..views.album_view import AlbumView
from ..views.artist_view import ArtistView
from ..views.base_view import BaseView
from ..views.list_view import ListView
from ..views.playlist_view import PlaylistView
from ..views.user_view import UserView


class FamilyActions(BaseActions):
    """Holds actions for family related browsing"""

    @classmethod
    def index(cls):
        """Displays the family profiles"""
        response = Api.instance().request('user', 'me', 'followings')
        return ListView(UserView, response)

    @classmethod
    def show(cls, identifiant):
        """
        Displays the content of a family profile.

        :param identifiant: user ID
        """
        icons = cls.args.get('path') + '/resources/icons'

        return [
            BaseView({'path': '/family/{}/playlists'.format(identifiant)}, 'Playlists', True)
                .set_icon(icons + '/playlists.png'),
            BaseView({'path': '/family/{}/albums'.format(identifiant)}, 'Albums', True)
                .set_icon(icons + '/albums.png'),
            BaseView({'path': '/family/{}/artists'.format(identifiant)}, 'Artists', True)
                .set_icon(icons + '/artists.png')
        ]

    @classmethod
    def playlists(cls, identifiant):
        """
        Displays the playlists of a family profile.

        :param identifiant: user ID
        """
        response = Api.instance().request('user', identifiant, 'playlists')
        return ListView(PlaylistView, response)

    @classmethod
    def albums(cls, identifiant):
        """
        Displays the albums of a family profile

        :param identifiant: user ID
        """
        response = Api.instance().request('user', identifiant, 'albums')
        return ListView(AlbumView, response)

    @classmethod
    def artists(cls, identifiant):
        """
        Displays the artists of a family profile

        :param identifiant: user ID
        """
        response = Api.instance().request('user', identifiant, 'artists')
        return ListView(ArtistView, response)
