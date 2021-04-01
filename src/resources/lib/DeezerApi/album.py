# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcplugin

from .deezer_object import DeezerObject


class Album(DeezerObject):
    """
    Deezer Album. List of track with a cover.
    """

    def get_tracks(self):
        """
        Return the track list of the album.

        :return: List of Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: Getting tracks of album id {}".format(self.id), xbmc.LOGDEBUG)
        tracks = []

        for tr in self.tracks['data']:
            if tr['readable']:
                tracks.append(Track(self.connection, tr))

        return tracks

    def get_artist(self):
        """
        Return the artist of this album.

        :return: An Artist object
        """
        from .artist import Artist
        xbmc.log("DeezerKodi: Getting artist of album id {}".format(self.id), xbmc.LOGDEBUG)
        return Artist(self.connection, self.artist)

    def get_cover(self, size=''):
        """
        Return the url to the cover of the album.

        :param str size: Size of the cover, can be [small, medium, big, xl]
        :return: The url of the cover
        """
        xbmc.log("DeezerKodi: Trying to get album cover of size " + size, xbmc.LOGDEBUG)

        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'cover_' + size):
            return self.__dict__['cover_' + size]

        if size == '' and hasattr(self, 'cover'):
            return self.cover

        return ''

    def listItem(self):
        """
        Returns this album as a ListItem

        :return: xbmcgui.ListItem
        """
        li = xbmcgui.ListItem(self.title)
        li.setArt({
            'thumb': self.get_cover('big'),
            'icon': self.get_cover('small')
        })
        return li

    def listItems(self):
        """
        Return the current album as a list of ListItem

        :return: list( xbmcgui.ListItem )
        """
        from .build_url import build_url
        items = []

        for track in self.get_tracks():
            li = track.listItem()
            li.setProperty('IsPlayable', 'true')

            url = build_url({'mode': 'track', 'id': track.id, 'container': 'album'})

            items.append((url, li))

        return items

    def display(self, end=True):
        """
        Display Album as a kodi listing.\n
        An Album consists of a list of tracks.

        :param bool end: Set if the method gives back focus to kodi
            True by default
        """
        from .build_url import addon_handle
        xbmc.log("DeezerKodi: Displaying album ...", xbmc.LOGDEBUG)

        items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'songs')

        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of album display", xbmc.LOGDEBUG)
