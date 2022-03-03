from app.views.base_view import BaseView


class AlbumView(BaseView):
    """Defines a viewable album"""

    def __init__(self, data):
        BaseView.__init__(self, {'path': '/albums/{}'.format(data['id'])}, data['title'], True)
        self._item.setArt({
            'thumb': data.get('cover_big'),
            'icon': data.get('cover_small')
        })
