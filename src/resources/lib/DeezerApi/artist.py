# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcplugin

from .deezer_object import DeezerObject


class Artist(DeezerObject):
    """
    Deezer Artist object. Has a collection of album, a top, ...
    """

    def get_albums(self):
        """
        Return all albums from this artist.
        :return: List of Album
        """
        from .album import Album
        xbmc.log("DeezerKodi: Getting albums of artist id {}".format(self.id), xbmc.LOGDEBUG)
        albums = []

        albums_response = self.connection.make_request('artist', self.id, 'albums');

        for a in albums_response['data']:
            albums.append(Album(self.connection, a))

        return albums

    def get_top(self):
        """
        Return the top tracks for this artist.

        :return: List of Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: Getting top tracks of artist id {}".format(self.id), xbmc.LOGDEBUG)
        top = []

        for tr in self.connection.make_request('artist', self.id, 'top')['data']:
            top.append(Track(self.connection, tr))

        return top

    def get_picture(self, size=''):
        """
        Return the url to the picture of the artist.

        :param str size: Size of the picture, can be [small, medium, big, xl]
        :return: The url of the picture
        """
        xbmc.log(
            "DeezerKodi: Trying to get picture of artist id {id} with size {size}".format(
                id=self.id,
                size=size
            ),
            xbmc.LOGDEBUG
        )

        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'picture_' + size):
            return self.__dict__['picture_' + size]

        if size == '' and hasattr(self, 'picture'):
            return self.picture

        return ''

    def listItem(self):
        """
        Returns the Artist representation in menus

        :return: ListItem
        """
        li = xbmcgui.ListItem(self.name)
        li.setArt({
            'thumb': self.get_picture('big'),
            'icon': self.get_picture('small'),
        })
        return li

    def listItems(self):
        """
        Returns the content of this artist (albums)

        :return: a list of ListItem
        """
        from .build_url import build_url
        items = []

        for album in self.get_albums():
            li = album.listItem()
            url = build_url({'mode': 'album', 'id': album.id})
            items.append((url, li, True))

        return items

    def display(self, end=True):
        """
        Display Artist as a kodi listing.\n
        An Artist consists of a top and a list of albums (for now).

        :param bool end: Set if the method gives back focus to kodi
            True by default
        """
        from .build_url import addon_handle
        xbmc.log("DeezerKodi: Displaying artist ...", xbmc.LOGDEBUG)

        items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'artists')

        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of artist display", xbmc.LOGDEBUG)
