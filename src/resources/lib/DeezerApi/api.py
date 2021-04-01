# -*- coding: utf-8 -*-

import xbmc


class Api(object):
    """
    Api class. Allows to query for Deezer object easily from the API.
    """

    def __init__(self, connection):
        """
        Instatiate an Api object with a connection to Deezer.

        :param Connection connection: A Connection to Deezer
        """
        xbmc.log("DeezerKodi: API: Creating API instance", xbmc.LOGDEBUG)
        self.connection = connection

    def get_user(self, id):
        """
        Return the user with the given `id`.

        :param str id: ID of the user
        :return: A User
        """
        from .user import User
        xbmc.log("DeezerKodi: API: Getting user id {} from API".format(id), xbmc.LOGDEBUG)
        return User(self.connection, self.connection.make_request('user', id))

    def get_playlist(self, id):
        """
        Return the playlist with the given `id`.

        :param int id: ID of the playlist
        :return: A Playlist
        """
        from .playlist import Playlist
        xbmc.log("DeezerKodi: API: Getting playlist id {} from API".format(id), xbmc.LOGDEBUG)
        return Playlist(self.connection, self.connection.make_request('playlist', id))

    def get_track(self, id):
        """
        Return the track with the given `id`.

        :param int id: ID of the track
        :return: A Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: API: Getting track id {} from API".format(id), xbmc.LOGDEBUG)
        return Track(self.connection, self.connection.make_request('track', id))

    def get_album(self, id):
        """
        Return the album with the given `id`.

        :param int id: ID of the album
        :return: An Album
        """
        from .album import Album
        xbmc.log("DeezerKodi: API: Getting album id {} from API".format(id), xbmc.LOGDEBUG)
        return Album(self.connection, self.connection.make_request('album', id))

    def get_artist(self, id):
        """
        Return the artist with the given `id`.

        :param int id: ID of the artist
        :return: An Artist
        """
        from .artist import Artist
        xbmc.log("DeezerKodi: API: Getting artist id {} from API".format(id), xbmc.LOGDEBUG)
        return Artist(self.connection, self.connection.make_request('artist', id))

    def search(self, query, filter):
        """
        Search for `query`. Add filter to search by track, album, ...

        :param str query: The text to search
        :param str filter: Type of object to search. May be one of
            [album, artist, history, playlist, podcast, radio, track, user]
        :return:
        """
        from .search import Search
        xbmc.log(
            "DeezerKodi: API: Searching {query} with filter {filter}".format(query=query, filter=filter),
            xbmc.LOGDEBUG
        )
        result = self.connection.make_request('search', method=filter, parameters={'q': query})
        return Search(self.connection, result, filter)
