# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcplugin

from ..deezer_exception.deezer_exception import DeezerException
from .build_url import build_url, addon_handle


class Search(object):
    """
    Deezer Search. List of searched item (tracks, albums, artists, ...)
    """

    def __init__(self, connection, content, search_type):
        """
        Instantiate a Search with a connection, data and a search type.

        :param Connection connection: Connection to the API
        :param dict content: Object's content, as returned by the API
        :param str search_type: Type of search made. May be [track, album, artist] (for now)
        """
        xbmc.log("DeezerKodi: Creating a search of type " + search_type, xbmc.LOGDEBUG)
        self.connection = connection
        self.__dict__.update(content)
        self.search_type = search_type

    def display(self):
        """
        Display the results of the search according to its type.
        """
        if self.search_type == 'track':
            self.__display_tracks()

        elif self.search_type == 'album':
            self.__display_albums()

        elif self.search_type == 'artist':
            self.__display_artists()

        else:
            raise DeezerException("Invalid search type, cannot display result")

    def __display_tracks(self):
        """
        Display tracks returned by the research.
        """
        from .track import Track
        xbmc.log("DeezerKodi: Displaying tracks search result ...", xbmc.LOGDEBUG)
        items = []

        for tr in self.data:
            track_obj = Track(self.connection, tr)
            track_album = track_obj.get_album()

            li = xbmcgui.ListItem(track_obj.title)
            li.setInfo('music', {
                'duration': track_obj.duration,
                'album': track_album.title,
                'artist': track_obj.get_artist().name,
                'title': track_obj.title,
                'mediatype': 'song'
            })
            li.setArt({
                'thumb': track_album.get_cover('big'),
                'icon': track_album.get_cover('small')
            })

            url = build_url({'mode': 'searched_track', 'id': track_obj.id})

            items.append((url, li))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'songs')
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log("DeezerKodi: End of tracks search result display", xbmc.LOGDEBUG)

    def __display_albums(self):
        """
        Display albums returned by the research.
        """
        from .album import Album
        xbmc.log("DeezerKodi: Displaying albums search result ...", xbmc.LOGDEBUG)
        items = []

        for al in self.data:
            album_obj = Album(self.connection, al)

            li = album_obj.listItem()
            url = build_url({'mode': 'album', 'id': album_obj.id})
            items.append((url, li, True))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'albums')
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log("DeezerKodi: End of albums search result display", xbmc.LOGDEBUG)

    def __display_artists(self):
        """
        Display artists returned by the research.
        """
        from .artist import Artist
        xbmc.log("DeezerKodi: Displaying artists search result ...", xbmc.LOGDEBUG)
        items = []

        for ar in self.data:
            artist_obj = Artist(self.connection, ar)

            li = xbmcgui.ListItem(artist_obj.name)
            li.setArt({
                'thumb': artist_obj.get_picture('big'),
                'icon': artist_obj.get_picture('small')
            })

            url = build_url({'mode': 'artist', 'id': artist_obj.id})

            items.append((url, li, True))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'albums')
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log("DeezerKodi: End of artists search result display", xbmc.LOGDEBUG)
