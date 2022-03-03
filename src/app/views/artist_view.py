from app.views.base_view import BaseView


class ArtistView(BaseView):
    """Displayable artist"""

    def __init__(self, data):
        BaseView.__init__(self, {'path': '/artists/{}'.format(data['id'])}, data['name'], True)
        self._item.setArt({
            'thumb': data['picture_big'],
            'icon': data['picture_small'],
        })
