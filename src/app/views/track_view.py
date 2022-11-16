from datetime import datetime

from app.views.base_view import BaseView


class TrackView(BaseView):
    """
    Defines a viewable track in Kodi
    A track has a duration, artist, album, cover, etc
    """

    def __init__(self, data):
        BaseView.__init__(
            self,
            {'path': '/tracks/{}/play'.format(data['id'])},
            data['title'],
            False
        )

        self._item.setInfo('music', {
            'duration': data['duration'],
            'album': data.get('album', {}).get('title'),
            'artist': data.get('artist', {}).get('name'),
            'title': data['title'],
            'date': datetime.fromtimestamp(data['time_add']).strftime("%d.%m.%Y"),
            'mediatype': 'song'
        })
        self._item.setArt({
            'thumb': data.get('album', {}).get('cover_big'),
            'icon': data.get('album', {}).get('cover_small')
        })
        self._item.setProperty('IsPlayable', 'true')
