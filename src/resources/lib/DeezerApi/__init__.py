# -*- coding: utf-8 -*-

import hashlib
import json
import pickle

import requests
import xbmc

from ..deezer_exception import QuotaException, DeezerException

from .album import Album
from .api import Api
from .artist import Artist
from .build_url import *
from .deezer_object import DeezerObject
from .playlist import Playlist
from .search import Search
from .track import Track
from .user import User


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

        url = self._API_BASE_URL.format(service=service, id=id, method=method)
        response = requests.get(url, params=self._merge_two_dicts(
            {'output': 'json', 'access_token': self._access_token}, parameters
        ))

        response = json.loads(response.text)

        # if there is a next url, call it
        if 'next' in response:
            response['data'] += Connection.make_request_url(response['next'])['data']

        return response

    @staticmethod
    def make_request_url(url):
        """
        Send a GET request to `url`.

        :param str url: Url to query
        :return: JSON response as dict
        """
        xbmc.log('DeezerKodi: Connection: Making custom request ...', xbmc.LOGDEBUG)
        response = requests.get(url)

        response = json.loads(response.text)

        # if there is a next url, call it and append data
        if 'next' in response:
            response['data'] += Connection.make_request_url(response['next'])['data']

        return response

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
