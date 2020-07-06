# -*- coding: utf-8 -*-

import requests
import urllib
import sys
import hashlib
import json
import pickle

import xbmc
import xbmcgui
import xbmcplugin


base_url = sys.argv[0]


def build_url(query):
    """
    Build url from `query` dict.
    Used to build url to navigate in menus.

    :param dict query: Options to add in the url
    :return: The encoded url as str
    """
    return base_url + '?' + urllib.urlencode(query)


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

    def _obtain_access_token(self):
        """
        Obtain access token by pretending to be a smart tv.

        :raise Exception: In case of error returned by the API
        """
        if self._username is None or self._password is None:
            raise Exception("Username and password is required!")
        r = requests.get(self._API_AUTH_URL, params={
                'login': self._username,
                'password': self._password,
                'device': 'panasonic'
        })
        response = r.json()
        if 'access_token' in response:
            self._access_token = response['access_token']
        else:
            if 'error' in response:
                error = response['error']
                raise Exception(error['message'])
            else:
                raise Exception("Could not obtain access token!")

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
        Make request to the API and return response as a dict.
        Parameters names are same as described in the Deezer API documentation (https://developers.deezer.com/api).

        :param str service:     The service to request
        :param str id:          Item's ID in the service
        :param str method:      Service method
        :param dict parameters: Additional parameters at the end
        :return:                JSON response as dict
        """
        base_url = self._API_BASE_URL.format(service=service, id=id, method=method)
        r = requests.get(base_url, params=self._merge_two_dicts(
                {'output': 'json', 'access_token': self._access_token}, parameters
        ))
        return json.loads(r.text)

    @staticmethod
    def make_request_url(url):
        """
        Send a GET request to `url`.

        :param str url: Url to query
        :return: JSON response as dict
        """
        r = requests.get(url)
        return json.loads(r.text)

    def make_request_streaming(self, id='', type='track'):
        """
        Make a request to get the streaming url of `type` with `id`.

        :param str id: ID of the requested item
        :param str type: Type of the requested item
        :return: Dict if type is radio or artist, str otherwise
        """
        r = requests.get(self._API_BASE_STREAMING_URL, params={
                'access_token': self._access_token,
                ("%s_id" % type): id,
                'device': 'panasonic'
        })
        if type.startswith('radio') or type.startswith('artist'):
            return json.loads(r.text)
        return r.text


class DeezerObject(object):
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
    def get_playlists(self):
        """
        Return the user's playlists.

        :return: A list of Playlist
        """
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
        artists = []
        artists_data = self.connection.make_request('user', self.id, 'recommendations/artists')

        for track in artists_data['data']:
            artists.append(Artist(self.connection, track))

        return artists


class Playlist(DeezerObject):
    """
    Deezer Playlist. A list of tracks with a playlist picture.
    """
    def get_tracks(self, next_url=None):
        """
        Return playlist's tracks.

        :param str next_url: Url of the next part of the playlist, used for recursion. Shouldn't be used otherwise.
        :return: A list of Track
        """
        tracks = []

        if next_url is not None:
            tracks_data = self.connection.make_request_url(next_url)
        elif hasattr(self, 'tracks'):
            tracks_data = self.tracks
        else:
            tracks_data = self.connection.make_request('playlist', self.id, 'tracks')

        for track in tracks_data['data']:
            tracks.append(Track(self.connection, track))

        if 'next' in tracks_data:
            tracks += self.get_tracks(tracks_data['next'])

        return tracks

    def save(self):
        """
        Save the playlist to a file in kodi special temp folder.\n
        Used for adding playlist to queue without querying API again.
        """
        with open(xbmc.translatePath('special://temp/playlist.pickle'), 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        """
        Load a playlist from a file in kodi special temp folder.

        :return: a Playlist object
        """
        with open(xbmc.translatePath('special://temp/playlist.pickle'), 'rb') as f:
            cls = pickle.load(f)
        return cls

    def get_picture(self, size=''):
        """
        Return the url to the picture of the playlist.

        :param str size: Size of the picture, can be [small, medium, big, xl]
        :return: The url of the picture
        """
        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'cover_'+size):
            pic = self.__dict__['picture_'+size]
        elif size == '' and hasattr(self, 'picture'):
            pic = self.picture
        else:
            pic = ''

        return pic


class Track(DeezerObject):
    """
    Deezer Track.
    """
    def get_album(self):
        """
        Return the album of the track.

        :return: Album object
        """
        if not hasattr(self, 'album'):
            self._update_data()

        return Album(self.connection, self.album)

    def get_artist(self):
        """
        Return the artist of the track.

        :return: Artist object
        """
        return Artist(self.connection, self.artist)

    def get_alternative(self):
        """
        Return an alternative track. Useful if the current one is unavailable.

        :return: Track object
        """
        if not hasattr(self, 'alternative'):
            self._update_data()

        return Track(self.connection, self.alternative)


class Album(DeezerObject):
    """
    Deezer Album. List of track with a cover.
    """
    def get_tracks(self):
        """
        Return the track list of the album.

        :return: List of Track
        """
        tracks = []

        for track in self.tracks['data']:
            tracks.append(Track(self.connection, track))

        return tracks

    def get_cover(self, size=''):
        """
        Return the url to the cover of the album.

        :param str size: Size of the cover, can be [small, medium, big, xl]
        :return: The url of the cover
        """
        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'cover_'+size):
            cover = self.__dict__['cover_'+size]
        elif size == '' and hasattr(self, 'cover'):
            cover = self.cover
        else:
            cover = ''

        return cover


class Artist(DeezerObject):
    """
    Deezer Artist object. Has a collection of album, a top, ...
    """
    def get_albums(self):
        """
        Return all albums from this artist.

        :return: List of Album
        """
        albums = []

        for a in self.connection.make_request('artist', self.id, 'albums')['data']:
            albums.append(Album(self.connection, a))

        return albums

    def get_top(self):
        """
        Return the top tracks for this artist.

        :return: List of Track
        """
        top = []

        for track in self.connection.make_request('artist', self.id, 'top')['data']:
            top.append(Track(self.connection, track))

        return top


class Search(object):
    """
    Deezer Search. List of searched item (tracks, albums, artists, ...)
    """
    def __init__(self, connection, content, type):
        """
        Instantiate a Search with a connection, data and a type.

        :param Connection connection: Connection to the API
        :param dict content: Object's content, as returned by the API
        :param str type: Type of search made. May be [track, album, artist] (for now)
        """
        self.connection = connection
        self.__dict__.update(content)
        self.type = type

    def display(self, addon_handle):
        """
        Display the results of the search according to its type.

        :param int addon_handle: Handle of the addon
        """
        if self.type == 'track':
            self.__display_tracks(addon_handle)
        elif self.type == 'album':
            self.__display_albums(addon_handle)
        elif self.type == 'artist':
            self.__display_artists(addon_handle)

    def __display_tracks(self, addon_handle):
        """
        Display tracks returned by the research.

        :param addon_handle: Handle of the addon
        """
        items = []

        for tr in self.data:
            track = Track(self.connection, tr)
            track_album = track.get_album()

            li = xbmcgui.ListItem(track.title)
            li.setInfo('music', {
                    'duration': track.duration,
                    'album': track_album.title,
                    'artist': track.get_artist().name,
                    'title': track.title
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

    def __display_albums(self, addon_handle):
        """
        Display albums returned by the research.

        :param addon_handle: Handle of the addon
        """
        pass

    def __display_artists(self, addon_handle):
        """
        Display artists returned by the research.

        :param addon_handle: Handle of the addon
        """
        pass


class Api(object):
    """
    Api class. Allows to query for Deezer object easily from the API.
    """
    def __init__(self, connection):
        """
        Instatiate an Api object with a connection to Deezer.

        :param Connection connection: A Connection to Deezer
        """
        self.connection = connection

    def get_user(self, id):
        """
        Return the user with the given `id`.

        :param str id: ID of the user
        :return: A User
        """
        return User(self.connection, self.connection.make_request('user', id))

    def get_playlist(self, id):
        """
        Return the playlist with the given `id`.

        :param int id: ID of the playlist
        :return: A Playlist
        """
        return Playlist(self.connection, self.connection.make_request('playlist', id))

    def get_track(self, id):
        """
        Return the track with the given `id`.

        :param int id: ID of the track
        :return: A Track
        """
        return Track(self.connection, self.connection.make_request('track', id))

    def get_album(self, id):
        """
        Return the album with the given `id`.

        :param int id: ID of the album
        :return: An Album
        """
        return Album(self.connection, self.connection.make_request('album', id))

    def get_artist(self, id):
        """
        Return the artist with the given `id`.

        :param int id: ID of the artist
        :return: An Artist
        """
        return Artist(self.connection, self.connection.make_request('artist', id))

    def search(self, query, filter=""):
        """
        Search for `query`. Possibly add filter to search by track, album, ...
        TODO: Complete method and documentation

        :param str query: The text to search
        :param str filter: Type of object to search. May be one of
            [album, artist, history, playlist, podcast, radio, track, user]
        :return:
        """
        result = self.connection.make_request('search', method=filter, parameters={'q': query})
        return Search(self.connection, result, filter)
