# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcplugin

from .deezer_object import DeezerObject


class Playlist(DeezerObject):
    """
    Deezer Playlist. A list of tracks with a playlist picture.
    """

    def get_tracks(self):
        """
        Return playlist's tracks.
        :return: A list of Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: Getting playlist's tracks", xbmc.LOGDEBUG)

        tracks = []
        if hasattr(self, 'tracks') and len(self.tracks) == self.nb_tracks:
            tracks_data = self.tracks
        else:
            tracks_data = self.connection.make_request('playlist', self.id, 'tracks')

        for trk in tracks_data['data']:
            if trk['readable']:
                tracks.append(Track(self.connection, trk))

        tracks.reverse()
        return tracks

    def get_picture(self, size=''):
        """
        Return the url to the picture of the playlist.

        :param str size: Size of the picture, can be [small, medium, big, xl]
        :return: The url of the picture
        """
        xbmc.log("DeezerKodi: Trying to get playlist picture in size {}".format(size),
                 xbmc.LOGDEBUG)

        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'picture_' + size):
            return self.__dict__['picture_' + size]

        if size == '' and hasattr(self, 'picture'):
            return self.picture

        return ''

    def listItem(self):
        """
        Returns this playlist as a ListItem.

        :return: ListItem
        """
        li = xbmcgui.ListItem(self.title)
        li.setArt({
            'thumb': self.get_picture('big'),
            'icon': self.get_picture('small')
        })
        return li

    def listItems(self):
        """
        Returns the content of this playlist as a list of ListItem.

        :return: a list of ListItem
        """
        from .build_url import build_url
        items = []

        for track in self.get_tracks():
            li = track.listItem()
            li.setProperty('IsPlayable', 'true')

            url = build_url({'mode': 'track', 'id': track.id, 'container': 'playlist'})

            items.append((url, li))

        return items

    def display(self, end=True):
        """
        Display Playlist as a kodi listing.\n
        A Playlist consists of a list of tracks.

        :param bool end: Set if the method gives back focus to kodi
            True by default
        """
        from .build_url import addon_handle
        xbmc.log("DeezerKodi: Displaying playlist ...", xbmc.LOGDEBUG)

        items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'songs')
        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of playlist display", xbmc.LOGDEBUG)
