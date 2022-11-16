from .base_actions import BaseActions
from ..http import Api
from ..views.album_view import AlbumView
from ..views.base_view import BaseView
from ..views.list_view import ListView
from ..views.track_view import TrackView


class ArtistsActions(BaseActions):
    """Holds artist related actions"""

    @classmethod
    def show(cls, identifiant):
        """
        Shows an artist's content. His albums, top tracks etc

        :param identifiant: artist's ID
        """
        icons = cls.app.args().get('path') + '/resources/icons'

        return [
            BaseView({'path': '/artists/{}/top'.format(identifiant)}, 'Top', True)
            .set_icon(icons + '/chart.png'),
            BaseView({'path': '/artists/{}/albums'.format(identifiant)}, 'Albums', True)
            .set_icon(icons + '/albums.png'),
        ]

    @classmethod
    def top(cls, identifiant):
        """
        Gets the top tracks of an artist.

        :param identifiant: artist's ID
        :return: The artist's top tracks
        """
        response = Api.instance().request('artist', identifiant, 'top')
        return ListView(TrackView, response)

    @classmethod
    def albums(cls, identifiant):
        """
        Gets the albums of an artist.

        :param identifiant: Artist's ID
        :return: ListView of albums
        """
        response = Api.instance().request('artist', identifiant, 'albums')
        return ListView(AlbumView, response)
