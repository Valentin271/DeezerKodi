# -*- coding: utf-8 -*-

import requests
import hashlib
import json
import logging
import pickle
import xbmc


class Connection(object):
    """
    Connection class holds user login and password.
    It is responsible for obtaining access_token automatically when a request is made
    """

    _API_BASE_URL = "http://api.deezer.com/2.0/{service}/{id}/{method}"
    _API_BASE_STREAMING_URL = "http://tv.deezer.com/smarttv/streaming.php"
    _API_AUTH_URL = "http://tv.deezer.com/smarttv/authentication.php"

    def __init__(self, username, password):
        self._username = self._password = self._access_token = None
        self.set_username(username)
        self.set_password(password)
        self._obtain_access_token()

    def set_username(self, username):
        """save username"""
        self._username = username

    def set_password(self, password):
        """save md5 of user password"""
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        self._password = md5.hexdigest()

    def _obtain_access_token(self):
        """obtain access token by pretending to be a smart tv"""
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
        """Given two dicts, merge them into a new dict as a shallow copy."""
        z = x.copy()
        z.update(y)
        return z

    def make_request(self, service, id='', method='', parameters={}):
        """make request to the api and return response as a dict"""
        base_url = self._API_BASE_URL.format(service=service, id=id, method=method)
        logging.debug("make_request: %s | %s", base_url, parameters)
        r = requests.get(base_url, params=self._merge_two_dicts(
                {'output': 'json', 'access_token': self._access_token}, parameters
        ))
        return json.loads(r.text)

    @staticmethod
    def make_request_url(url):
        r = requests.get(url)
        return json.loads(r.text)

    def make_request_streaming(self, id='', type='track'):
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
        self.connection = connection
        self.__dict__.update(object_content)

    def _update_data(self):
        data = self.connection.make_request(self.type, self.id)
        self.__dict__.update(data)


class User(DeezerObject):
    def get_playlists(self):
        playlists = []
        playlists_data = self.connection.make_request('user', self.id, 'playlists')

        for lst in playlists_data['data']:
            playlists.append(Playlist(self.connection, lst))

        return playlists

    def get_followings(self):
        followings = []
        friends = self.connection.make_request('user', self.id, 'followings')

        for friend in friends['data']:
            followings.append(User(self.connection, friend))

        return followings

    def get_flow(self):
        flow = []
        flow_data = self.connection.make_request('user', self.id, 'flow')

        for track in flow_data['data']:
            flow.append(Track(self.connection, track))

        return flow

    def get_history(self):
        history = []
        history_data = self.connection.make_request('user', self.id, 'history')

        for track in history_data['data']:
            history.append(Track(self.connection, track))

        return history

    def get_recommended_tracks(self):
        tracks = []
        tracks_data = self.connection.make_request('user', self.id, 'recommendations/tracks')

        for track in tracks_data['data']:
            tracks.append(Track(self.connection, track))

        return tracks

    def get_recommended_playlists(self):
        playlists = []
        playlist_data = self.connection.make_request('user', self.id, 'recommendations/playlists')

        for track in playlist_data['data']:
            playlists.append(Track(self.connection, track))

        return playlists

    def get_recommended_artists(self):
        artists = []
        artists_data = self.connection.make_request('user', self.id, 'recommendations/artists')

        for track in artists_data['data']:
            artists.append(Track(self.connection, track))

        return artists


class Playlist(DeezerObject):
    def get_tracks(self, next_url=None):
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
        with open(xbmc.translatePath('special://temp/playlist.pickle'), 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        with open(xbmc.translatePath('special://temp/playlist.pickle'), 'rb') as f:
            cls = pickle.load(f)
        return cls

    def get_picture(self, size=''):
        """
        size [small, medium, big, xl]
        """
        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'cover_'+size):
            pic = self.__dict__['picture_'+size]
        elif size == '' and hasattr(self, 'picture'):
            pic = self.picture
        else:
            pic = ''

        return pic


class Track(DeezerObject):
    def get_album(self):
        if not hasattr(self, 'album'):
            self._update_data()

        return Album(self.connection, self.album)

    def get_artist(self):
        return Artist(self.connection, self.artist)

    def get_alternative(self):
        if not hasattr(self, 'alternative'):
            self._update_data()

        return Track(self.connection, self.alternative)


class Album(DeezerObject):
    def get_tracks(self):
        tracks = []

        for track in self.tracks['data']:
            tracks.append(Track(self.connection, track))

        return tracks

    def get_cover(self, size=''):
        """
        size [small, medium, big, xl]
        """
        if size in ['small', 'medium', 'big', 'xl'] and hasattr(self, 'cover_'+size):
            cover = self.__dict__['cover_'+size]
        elif size == '' and hasattr(self, 'cover'):
            cover = self.cover
        else:
            cover = ''

        return cover


class Artist(DeezerObject):
    def get_albums(self):
        albums = []

        for a in self.connection.make_request('artist', self.id, 'albums')['data']:
            albums.append(Album(self.connection, a))

        return albums

    def get_top(self):
        top = []

        for track in self.connection.make_request('artist', self.id, 'top')['data']:
            top.append(Track(self.connection, track))

        return top


class Search(DeezerObject):
    def get_listing(self):
        pass


class Api(object):
    def __init__(self, connection):
        self.connection = connection

    def get_user(self, id):
        return User(self.connection, self.connection.make_request('user', id))

    def get_playlist(self, id):
        return Playlist(self.connection, self.connection.make_request('playlist', id))

    def get_track(self, id):
        return Track(self.connection, self.connection.make_request('track', id))

    def get_album(self, id):
        return Album(self.connection, self.connection.make_request('album', id))

    def get_artist(self, id):
        return Artist(self.connection, self.connection.make_request('artist', id))

    def search(self, query, filter=""):
        self.connection.make_request('search', method=filter, parameters={'q': query})
