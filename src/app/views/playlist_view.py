from app.views.base_view import BaseView


class PlaylistView(BaseView):
    """Represents a playlist displayable by Kodi"""

    def __init__(self, data):
        BaseView.__init__(self, {'path': '/playlists/{}'.format(data['id'])}, data['title'], True)
        self._item.setArt({
            'thumb': data.get('picture_big'),
            'icon': data.get('picture_small')
        })
