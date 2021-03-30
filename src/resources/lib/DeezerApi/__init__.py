# -*- coding: utf-8 -*-

import hashlib
import json
import pickle
import sys

# Python3
try:
    from urllib.parse import urlencode

# Python2
except ImportError:
    from urllib import urlencode

import requests
import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.deezer_exception import QuotaException, DeezerException

addon_handle = int(sys.argv[1])

base_url = sys.argv[0]


def build_url(query):
    """
    Build url from `query` dict.
    Used to build url to navigate in menus.

    :param dict query: Options to add in the url
    :return: The encoded url as str
    """
    for k, v in query.items():
        # Python2
        try:
            if isinstance(v, unicode):
                query[k] = v.encode('utf-8')
        # Python3
        except NameError:
            pass

    return base_url + '?' + urlencode(query)


class Connection(object):
    """
    Connection class holds user login and password.
    It is responsible for obtaining access_token automatically when a request is made
    """

    _API_BASE_URL = "http://api.deezer.com/2.0/{service}/{id}/{method}"
    _API_BASE_STREAMING_URL = "http://tv.deezer.com/smarttv/streaming.php"
    _API_AUTH_URL = "http://tv.deezer.com/smarttv/authentication.php"

    def __init__(self, username, password):
        """
        Instantiate a Connection object from username and password.

        :param str username: The user's name
        :param str password: The user's password
        """
        xbmc.log('DeezerKodi: Connection: Creating new connection ...', xbmc.LOGDEBUG)
        self._username = self._password = self._access_token = None
        self.set_username(username)
        self.set_password(password)
        self._obtain_access_token()

    def set_username(self, username):
        """
        Set username.

        :param str username: The user's name to set
        """
        self._username = username

    def set_password(self, password):
        """
        Save md5 of user password.

        :param str password: The user's password to save
        """
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        self._password = md5.hexdigest()

    def save(self):
        """
        Save the connection to a file in kodi special temp folder.
        """
        path = xbmc.translatePath('special://temp/connection.pickle')
        xbmc.log("DeezerKodi: Connection: Saving connection to file {}".format(path), xbmc.LOGDEBUG)

        with open(path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        """
        Load a connection from a file in kodi special temp folder.

        :return: a Connection object
        """
        path = xbmc.translatePath('special://temp/connection.pickle')
        xbmc.log("DeezerKodi: Connection: Getting connection from file {}".format(path), xbmc.LOGDEBUG)

        with open(path, 'rb') as f:
            cls = pickle.load(f)
        return cls

    def _obtain_access_token(self):
        """
        Obtain access token by pretending to be a smart tv.

        :raise Exception: In case of error returned by the API
        """
        xbmc.log('DeezerKodi: Connection: Getting access token ...', xbmc.LOGDEBUG)
        if self._username is None or self._password is None:
            raise Exception("Username and password are required!")
        response = requests.get(self._API_AUTH_URL, params={
            'login': self._username,
            'password': self._password,
            'device': 'panasonic'
        })
        json_response = response.json()
        if 'access_token' in json_response:
            self._access_token = json_response['access_token']
        else:
            if 'error' in json_response and json_response['error']['code'] == QuotaException.CODE:
                raise QuotaException(json_response['error']['message'])
            else:
                raise DeezerException("Could not obtain access token!")

    @staticmethod
    def _merge_two_dicts(x, y):
        """
        Given two dicts, merge them into a new dict as a shallow copy.

        :param dict x: First dict
        :param dict y: Second dict
        :return: Merged dict
        """
        z = x.copy()
        z.update(y)
        return z

    def make_request(self, service, id='', method='', parameters={}):
        """
        Make request to the API and return response as a dict.\n
        Parameters names are the same as described in
        the Deezer API documentation (https://developers.deezer.com/api).

        :param str service:     The service to request
        :param str id:          Item's ID in the service
        :param str method:      Service method
        :param dict parameters: Additional parameters at the end
        :return:                JSON response as dict
        """
        xbmc.log(
            'DeezerKodi: Connection: Requesting {} ...'.format(
                '/'.join([str(service), str(id), str(method)])),
            xbmc.LOGDEBUG
        )

        base_url = self._API_BASE_URL.format(service=service, id=id, method=method)
        response = requests.get(base_url, params=self._merge_two_dicts(
            {'output': 'json', 'access_token': self._access_token}, parameters
        ))
        return json.loads(response.text)

    @staticmethod
    def make_request_url(url):
        """
        Send a GET request to `url`.

        :param str url: Url to query
        :return: JSON response as dict
        """
        xbmc.log('DeezerKodi: Connection: Making custom request ...', xbmc.LOGDEBUG)
        response = requests.get(url)
        return json.loads(response.text)

    def make_request_streaming(self, id='', type='track'):
        """
        Make a request to get the streaming url of `type` with `id`.

        :param str id: ID of the requested item
        :param str type: Type of the requested item
        :return: Dict if type is radio or artist, str otherwise
        """
        xbmc.log(
            'DeezerKodi: Connection: Requesting streaming for {type} with id {id} ...'.format(
                type=type,
                id=id
            ),
            xbmc.LOGINFO
        )
        response = requests.get(self._API_BASE_STREAMING_URL, params={
            'access_token': self._access_token,
            "{}_id".format(type): id,
            'device': 'panasonic'
        })
        if type.startswith('radio') or type.startswith('artist'):
            return json.loads(response.text)
        return response.text


class DeezerObject(object):
    """
    Base class for any DeezerAPI class
    """

    def __init__(self, connection, object_content):
        """
        Instantiate a Deezer Object from a `connection` and the `content` of the object.

        :param Connection connection: Connection to the API
        :param dict object_content: Object's content, as returned by the API
        """
        self.connection = connection
        self.__dict__.update(object_content)

    def _update_data(self):
        """
        Update the current object with complete data.\n
        Sometimes the API return incomplete objects.
        """
        data = self.connection.make_request(self.type, self.id)
        self.__dict__.update(data)


class User(DeezerObject):
    """
    Deezer User. Represented by his playlists, followings, flow, history, recommendations, ...
    """

    def get_favourites_albums(self):
        """
        Return the user's favourites albums
        :return: A list of Album
        """
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
        xbmc.log("DeezerKodi: Getting user's flow", xbmc.LOGDEBUG)

        flow = []
        flow_data = self.connection.make_request('user', self.id, 'flow')

        for track in flow_data['data']:
            flow.append(Track(self.connection, track))

        return flow

    def get_history(self):
        """
        Return the user's history.

        :return: A list of Track
        """
        xbmc.log("DeezerKodi: Getting user's history", xbmc.LOGDEBUG)

        history = []
        history_data = self.connection.make_request('user', self.id, 'history')

        for track in history_data['data']:
            history.append(Track(self.connection, track))

        return history

    def get_recommended_tracks(self):
        """
        Return the recommended tracks for this user.

        :return: A list of Track
        """
        xbmc.log("DeezerKodi: Getting user's recommended tracks", xbmc.LOGDEBUG)

        tracks = []
        tracks_data = self.connection.make_request('user', self.id, 'recommendations/tracks')

        for track in tracks_data['data']:
            tracks.append(Track(self.connection, track))

        return tracks

    def get_recommended_playlists(self):
        """
        Return the recommended playlists for this user.

        :return: A list of Playlist
        """
        xbmc.log("DeezerKodi: Getting user's recommended playlists", xbmc.LOGDEBUG)

        playlists = []
        playlist_data = self.connection.make_request('user', self.id, 'recommendations/playlists')

        for track in playlist_data['data']:
            playlists.append(Playlist(self.connection, track))

        return playlists

    def get_recommended_artists(self):
        """
        Return the recommended artists for this user.

        :return: A list of Artist
        """
        xbmc.log("DeezerKodi: Getting user's recommended artists", xbmc.LOGDEBUG)

        artists = []
        artists_data = self.connection.make_request('user', self.id, 'recommendations/artists')

        for track in artists_data['data']:
            artists.append(Artist(self.connection, track))

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


class Playlist(DeezerObject):
    """
    Deezer Playlist. A list of tracks with a playlist picture.
    """

    def get_tracks(self, next_url=None):
        """
        Return playlist's tracks.

        :param str next_url: Url of the next part of the playlist, used for recursion.
            Shouldn't be used otherwise.
        :return: A list of Track
        """
        xbmc.log("DeezerKodi: Getting playlist's tracks", xbmc.LOGDEBUG)

        tracks = []

        if next_url is not None:
            tracks_data = self.connection.make_request_url(next_url)
        elif hasattr(self, 'tracks'):
            tracks_data = self.tracks
        else:
            tracks_data = self.connection.make_request('playlist', self.id, 'tracks')

        for track in tracks_data['data']:
            if track['readable']:
                tracks.append(Track(self.connection, track))

        if 'next' in tracks_data:
            tracks += self.get_tracks(tracks_data['next'])

        tracks.reverse()
        return tracks

    def get_picture(self, size=''):
        """
        Return the url to the picture of the playlist.

        :param str size: Size of the picture, can be [small, medium, big, xl]
        :return: The url of the picture
        """
        xbmc.log("DeezerKodi: Trying to get playlist picture in size {}".format(size), xbmc.LOGDEBUG)

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
        xbmc.log("DeezerKodi: Displaying playlist ...", xbmc.LOGDEBUG)

        items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'songs')
        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of playlist display", xbmc.LOGDEBUG)


class Track(DeezerObject):
    """
    Deezer Track.
    """

    def get_album(self):
        """
        Return the album of the track.

        :return: Album object
        """
        xbmc.log("DeezerKodi: Getting album of track id {}".format(self.id), xbmc.LOGDEBUG)
        if not hasattr(self, 'album'):
            self._update_data()

        return Album(self.connection, self.album)

    def get_artist(self):
        """
        Return the artist of the track.

        :return: Artist object
        """
        xbmc.log("DeezerKodi: Getting artist of track id {}".format(self.id), xbmc.LOGDEBUG)
        return Artist(self.connection, self.artist)

    def get_alternative(self):
        """
        Return an alternative track. Useful if the current one is unavailable.

        :return: Track object
        """
        xbmc.log("DeezerKodi: Getting alternative songs of track id {}".format(self.id), xbmc.LOGDEBUG)
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


class Album(DeezerObject):
    """
    Deezer Album. List of track with a cover.
    """

    def get_tracks(self):
        """
        Return the track list of the album.

        :return: List of Track
        """
        xbmc.log("DeezerKodi: Getting tracks of album id {}".format(self.id), xbmc.LOGDEBUG)
        tracks = []

        for track in self.tracks['data']:
            if track['readable']:
                tracks.append(Track(self.connection, track))

        return tracks

    def get_artist(self):
        """
        Return the artist of this album.

        :return: An Artist object
        """
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
        xbmc.log("DeezerKodi: Displaying album ...", xbmc.LOGDEBUG)

        items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'songs')

        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of album display", xbmc.LOGDEBUG)


class Artist(DeezerObject):
    """
    Deezer Artist object. Has a collection of album, a top, ...
    """

    def get_albums(self, next_url=None):
        """
        Return all albums from this artist.

        :param str next_url: Url of the next part of the playlist, used for recursion.
            Shouldn't be used otherwise.
        :return: List of Album
        """
        xbmc.log("DeezerKodi: Getting albums of artist id {}".format(self.id), xbmc.LOGDEBUG)
        albums = []

        if next_url is not None:
            albums_response = self.connection.make_request_url(next_url)
        else:
            albums_response = self.connection.make_request('artist', self.id, 'albums');

        for a in albums_response['data']:
            albums.append(Album(self.connection, a))

        if 'next' in albums_response:
            albums += self.get_albums(albums_response['next'])

        return albums

    def get_top(self):
        """
        Return the top tracks for this artist.

        :return: List of Track
        """
        xbmc.log("DeezerKodi: Getting top tracks of artist id {}".format(self.id), xbmc.LOGDEBUG)
        top = []

        for track in self.connection.make_request('artist', self.id, 'top')['data']:
            top.append(Track(self.connection, track))

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
        xbmc.log("DeezerKodi: Displaying artist ...", xbmc.LOGDEBUG)

        items = self.listItems()

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'artists')

        if end:
            xbmcplugin.endOfDirectory(addon_handle)
            xbmc.log("DeezerKodi: End of artist display", xbmc.LOGDEBUG)


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
        xbmc.log("DeezerKodi: Displaying tracks search result ...", xbmc.LOGDEBUG)
        items = []

        for tr in self.data:
            track = Track(self.connection, tr)
            track_album = track.get_album()

            li = xbmcgui.ListItem(track.title)
            li.setInfo('music', {
                'duration': track.duration,
                'album': track_album.title,
                'artist': track.get_artist().name,
                'title': track.title,
                'mediatype': 'song'
            })
            li.setArt({
                'thumb': track_album.get_cover('big'),
                'icon': track_album.get_cover('small')
            })

            url = build_url({'mode': 'searched_track', 'id': track.id})

            items.append((url, li))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'songs')
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log("DeezerKodi: End of tracks search result display", xbmc.LOGDEBUG)

    def __display_albums(self):
        """
        Display albums returned by the research.
        """
        xbmc.log("DeezerKodi: Displaying albums search result ...", xbmc.LOGDEBUG)
        items = []

        for al in self.data:
            album = Album(self.connection, al)

            li = album.listItem()
            url = build_url({'mode': 'album', 'id': album.id})
            items.append((url, li, True))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'albums')
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log("DeezerKodi: End of albums search result display", xbmc.LOGDEBUG)

    def __display_artists(self):
        """
        Display artists returned by the research.
        """
        xbmc.log("DeezerKodi: Displaying artists search result ...", xbmc.LOGDEBUG)
        items = []

        for ar in self.data:
            artist = Artist(self.connection, ar)

            li = xbmcgui.ListItem(artist.name)
            li.setArt({
                'thumb': artist.get_picture('big'),
                'icon': artist.get_picture('small')
            })

            url = build_url({'mode': 'artist', 'id': artist.id})

            items.append((url, li, True))

        xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
        xbmcplugin.setContent(addon_handle, 'albums')
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log("DeezerKodi: End of artists search result display", xbmc.LOGDEBUG)


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
        xbmc.log("DeezerKodi: API: Getting user id {} from API".format(id), xbmc.LOGDEBUG)
        return User(self.connection, self.connection.make_request('user', id))

    def get_playlist(self, id):
        """
        Return the playlist with the given `id`.

        :param int id: ID of the playlist
        :return: A Playlist
        """
        xbmc.log("DeezerKodi: API: Getting playlist id {} from API".format(id), xbmc.LOGDEBUG)
        return Playlist(self.connection, self.connection.make_request('playlist', id))

    def get_track(self, id):
        """
        Return the track with the given `id`.

        :param int id: ID of the track
        :return: A Track
        """
        xbmc.log("DeezerKodi: API: Getting track id {} from API".format(id), xbmc.LOGDEBUG)
        return Track(self.connection, self.connection.make_request('track', id))

    def get_album(self, id):
        """
        Return the album with the given `id`.

        :param int id: ID of the album
        :return: An Album
        """
        xbmc.log("DeezerKodi: API: Getting album id {} from API".format(id), xbmc.LOGDEBUG)
        return Album(self.connection, self.connection.make_request('album', id))

    def get_artist(self, id):
        """
        Return the artist with the given `id`.

        :param int id: ID of the artist
        :return: An Artist
        """
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
        xbmc.log(
            "DeezerKodi: API: Searching {query} with filter {filter}".format(query=query, filter=filter),
            xbmc.LOGDEBUG
        )
        result = self.connection.make_request('search', method=filter, parameters={'q': query})
        return Search(self.connection, result, filter)
