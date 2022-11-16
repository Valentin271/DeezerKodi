"""Defines generic app actions"""

from app.actions.base_actions import BaseActions
from app.views.base_view import BaseView


class HomeActions(BaseActions):
    """
    Holds generic app actions
    """

    @classmethod
    def index(cls):
        """
        Returns the main menu of the application.
        """
        icons = cls.app.args().get('path') + '/resources/icons'

        items = [
            BaseView({'path': '/family'}, 'Family', True),
            BaseView({'path': '/personal'}, 'Personal', True),
            BaseView({'path': '/search'}, 'Search', True)
            .set_icon(icons + '/search.png')
        ]

        return items
