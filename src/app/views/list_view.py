"""Defines the ListView class"""
from app.views.album_view import AlbumView
from app.views.artist_view import ArtistView
from app.views.track_view import TrackView


class ListView(list):
    """
    Class ListView represents a list of view.
    """

    # pylint: disable=line-too-long
    __CONTENT_TYPES = {
        TrackView: 'songs',
        ArtistView: '',  # should be artists
        # should be albums, but for some reason, setInfo doesn't work on albums and artists
        AlbumView: ''
    }
    """
    Content types from a view.
    See https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/group__python__xbmcplugin.html#gaa30572d1e5d9d589e1cd3bfc1e2318d6
    """

    # pylint: enable=line-too-long

    def __init__(self, view, items):
        """
        Creates a list of viewable item.

        :param view: The viewable items type inside the list. Inherited from BaseView.
        :param dict|list items: Items inside the list,
            can be a response containing a data key or directly a list.
        """
        list.__init__(self)

        self.content_type = ListView.__CONTENT_TYPES.get(view, '')

        for item in items['data'] if 'data' in items else items:
            self.append(view(item))
