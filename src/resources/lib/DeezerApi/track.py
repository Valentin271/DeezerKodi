# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

from .deezer_object import DeezerObject


class Track(DeezerObject):
    """
    Deezer Track.
    """

    def get_album(self):
        """
        Return the album of the track.

        :return: Album object
        """
        from .album import Album
        xbmc.log("DeezerKodi: Getting album of track id {}".format(self.id), xbmc.LOGDEBUG)
        if not hasattr(self, 'album'):
            self._update_data()

        return Album(self.connection, self.album)

    def get_artist(self):
        """
        Return the artist of the track.

        :return: Artist object
        """
        from .artist import Artist
        xbmc.log("DeezerKodi: Getting artist of track id {}".format(self.id), xbmc.LOGDEBUG)
        return Artist(self.connection, self.artist)

    def get_alternative(self):
        """
        Return an alternative track. Useful if the current one is unavailable.

        :return: Track object
        """
        xbmc.log("DeezerKodi: Getting alternative songs of track id {}".format(self.id),
                 xbmc.LOGDEBUG)
        if not hasattr(self, 'alternative'):
            self._update_data()

        return Track(self.connection, self.alternative)

    def listItem(self):
        """
        Returns a ListItem corresponding to this track

        :return: xbmcgui.ListItem
        """
        li = xbmcgui.ListItem(self.title)
        li.setInfo('music', {
            'duration': self.duration,
            'album': self.get_album().title,
            'artist': self.get_artist().name,
            'title': self.title,
            'mediatype': 'song'
        })
        li.setArt({
            'thumb': self.get_album().get_cover('big'),
            'icon': self.get_album().get_cover('small')
        })
        li.setProperty('IsPlayable', 'true')

        return li

    def play(self):
        """
        Play a song directly, do not put it in queue.
        """
        xbmc.log("DeezerKodi: Starting to play track id {}".format(self.id), xbmc.LOGDEBUG)
        url = self.connection.make_request_streaming(self.id, 'track')

        xbmc.Player().play(url, self.listItem())
