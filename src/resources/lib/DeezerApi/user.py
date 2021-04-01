# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcplugin

from .deezer_object import DeezerObject
from resources.lib.DeezerApi.build_url import build_url, addon_handle


class User(DeezerObject):
    """
    Deezer User. Represented by his playlists, followings, flow, history, recommendations, ...
    """

    def get_favourites_albums(self):
        """
        Return the user's favourites albums
        :return: A list of Album
        """
        from .album import Album
        xbmc.log("DeezerKodi: Getting user's favourites albums", xbmc.LOGDEBUG)

        albums = []
        response = self.connection.make_request('user', self.id, 'albums')

        for lst in response['data']:
            albums.append(Album(self.connection, lst))

        return albums

    def get_favourites_artists(self):
        """
        Return the user's favourites artists
        :return: A list of Artists
        """
        from .artist import Artist
        xbmc.log("DeezerKodi: Getting user's favourites artists", xbmc.LOGDEBUG)

        artists = []
        response = self.connection.make_request('user', self.id, 'artists')

        for lst in response['data']:
            artists.append(Artist(self.connection, lst))

        return artists

    def get_playlists(self):
        """
        Return the user's playlists.

        :return: A list of Playlist
        """
        from .playlist import Playlist
        xbmc.log("DeezerKodi: Getting user's playlists", xbmc.LOGDEBUG)

        playlists = []
        playlists_data = self.connection.make_request('user', self.id, 'playlists')

        for lst in playlists_data['data']:
            playlists.append(Playlist(self.connection, lst))

        return playlists

    def get_followings(self):
        """
        Return the user's followings.\n
        When User is the family main profile, can be used to gather family profiles.

        :return: A list of User
        """
        xbmc.log("DeezerKodi: Getting user's followings", xbmc.LOGDEBUG)

        followings = []
        friends = self.connection.make_request('user', self.id, 'followings')

        for friend in friends['data']:
            followings.append(User(self.connection, friend))

        return followings

    def get_flow(self):
        """
        Return the user's flow, tracks proposed by Deezer.

        :return: A list of Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: Getting user's flow", xbmc.LOGDEBUG)

        flow = []
        flow_data = self.connection.make_request('user', self.id, 'flow')

        for tr in flow_data['data']:
            flow.append(Track(self.connection, tr))

        return flow

    def get_history(self):
        """
        Return the user's history.

        :return: A list of Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: Getting user's history", xbmc.LOGDEBUG)

        history = []
        history_data = self.connection.make_request('user', self.id, 'history')

        for tr in history_data['data']:
            history.append(Track(self.connection, tr))

        return history

    def get_recommended_tracks(self):
        """
        Return the recommended tracks for this user.

        :return: A list of Track
        """
        from .track import Track
        xbmc.log("DeezerKodi: Getting user's recommended tracks", xbmc.LOGDEBUG)

        tracks = []
        tracks_data = self.connection.make_request('user', self.id, 'recommendations/tracks')

        for tr in tracks_data['data']:
            tracks.append(Track(self.connection, tr))

        return tracks

    def get_recommended_playlists(self):
        """
        Return the recommended playlists for this user.

        :return: A list of Playlist
        """
        from .playlist import Playlist
        xbmc.log("DeezerKodi: Getting user's recommended playlists", xbmc.LOGDEBUG)

        playlists = []
        playlist_data = self.connection.make_request('user', self.id, 'recommendations/playlists')

        for track_obj in playlist_data['data']:
            playlists.append(Playlist(self.connection, track_obj))

        return playlists

    def get_recommended_artists(self):
        """
        Return the recommended artists for this user.

        :return: A list of Artist
        """
        from .artist import Artist
        xbmc.log("DeezerKodi: Getting user's recommended artists", xbmc.LOGDEBUG)

        artists = []
        artists_data = self.connection.make_request('user', self.id, 'recommendations/artists')

        for track_obj in artists_data['data']:
            artists.append(Artist(self.connection, track_obj))

        return artists

    def listItem(self):
        """
        Returns this object representation in menus.

        :return: a list of ListItem
        """
        li = xbmcgui.ListItem(self.name)
        return li

    def listItems(self):
        """
        Returns the content of a User (playlists folder, albums folder, etc).

        :return: a list of ListItem
        """
        items = []

        # Playlists
        li = xbmcgui.ListItem('Playlists')
        url = build_url({'mode': 'user_playlist', 'id': self.id})
        items.append((url, li, True))

        # Albums
        li = xbmcgui.ListItem('Albums')
        url = build_url({'mode': 'user_album', 'id': self.id})
        items.append((url, li, True))

        # Artists
        li = xbmcgui.ListItem('Artists')
        url = build_url({'mode': 'user_artist', 'id': self.id})
        items.append((url, li, True))

        return items

    def albums_li(self):
        """
        Returns the user's favorite albums.

        :return: a list of ListItem
        """
        items = []

        for a in self.get_favourites_albums():
            li = a.listItem()
            url = build_url({'mode': 'album', 'id': a.id})
            items.append((url, li, True))

        return items

    def artists_li(self):
        """
        Returns the user's favorite artists.

        :return: a list of ListItem
        """
        items = []

        for a in self.get_favourites_artists():
            li = a.listItem()
            url = build_url({'mode': 'artist', 'id': a.id})
            items.append((url, li, True))

        return items

    def playlists_li(self):
        """
        Returns the user's playlists.

        :return: a list of ListItem
        """
        items = []

        for play in self.get_playlists():
            li = play.listItem()
            url = build_url({'mode': 'playlist', 'id': play.id})
            items.append((url, li, True))

        return items

    def display(self, mode='', end=True):
        """
        Display User as a kodi listing.\n
        A User consists of a list of playlist (for now).

        :param str mode: Whether to display the user content or his playlists, albums etc
        :param bool end: Set if the method gives back focus to kodi
            True by default
        """

        if mode == 'playlist':
            xbmc.log("DeezerKodi: Displaying user playlists ...", xbmc.LOGDEBUG)
            items = self.playlists_li()

        elif mode == 'album':
            xbmc.log("DeezerKodi: Displaying user albums ...", xbmc.LOGDEBUG)
            items = self.albums_li()

        elif mode == 'artist':
            xbmc.log("DeezerKodi: Displaying user artists ...", xbmc.LOGDEBUG)
            items = self.artists_li()

        else:
            xbmc.log("DeezerKodi: Displaying user ...", xbmc.LOGDEBUG)
            items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of user display", xbmc.LOGDEBUG)

    def display_family_profiles(self, end=True):
        """
        Display family profiles as a kodi listing.\n
        API doesn't give profiles, so instead followings are displayed.
        By default profiles are following the main account.

        :param bool end: Set if the method gives back focus to kodi
            True by default
        """
        xbmc.log("DeezerKodi: Displaying family profiles ...", xbmc.LOGDEBUG)

        items = []

        for user in self.get_followings():
            li = user.listItem()
            url = build_url({'mode': 'user_profile', 'id': user.id})
            items.append((url, li, True))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of family profile display", xbmc.LOGDEBUG)
