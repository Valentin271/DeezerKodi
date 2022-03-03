from app.actions.base_actions import BaseActions
from app.http import Api
from app.views.list_view import ListView
from app.views.track_view import TrackView


class AlbumsActions(BaseActions):
    """This class holds albums related actions"""

    @classmethod
    def show(cls, identifiant):
        """
        Displays the content of an album

        :param identifiant: album's ID
        :return: album's content
        """
        response = Api.instance().request('album', identifiant)

        for i, _ in enumerate(response['tracks']['data']):
            response['tracks']['data'][i]['album'] = {
                'title': response['title'],
                'cover_big': response.get('cover_big'),
                'cover_small': response.get('cover_small')
            }

        return ListView(TrackView, response['tracks'])
