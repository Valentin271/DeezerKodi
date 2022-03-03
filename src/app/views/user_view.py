from app.views.base_view import BaseView


class UserView(BaseView):
    """Defines a viewable user in Kodi"""

    def __init__(self, data):
        BaseView.__init__(self, {'path': '/family/{}'.format(data['id'])}, data['name'], True)
