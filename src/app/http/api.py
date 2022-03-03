# -*- coding: utf-8 -*-
"""
Provide a simple wrapper around Deezer API (with streaming).
"""

import hashlib
import pickle

import requests
import xbmc
import xbmcaddon
import xbmcvfs

from lib.exceptions import ApiExceptionFinder, CredentialsException
from lib.helpers.logger import Logger


class Api(object):
    """
    Api class holds user login and password.
    It is responsible for obtaining access_token automatically when a request is made
    """

    _API_BASE_URL = "http://api.deezer.com/2.0/{service}/{id}/{method}"
    _API_BASE_STREAMING_URL = "http://tv.deezer.com/smarttv/streaming.php"
    _API_AUTH_URL = "http://tv.deezer.com/smarttv/authentication.php"

    __CACHE_FILE = xbmc.translatePath('special://temp/deezer-api.pickle')

    __INSTANCE = None

    @classmethod
    def instance(cls):
        """
        Gets the running instance of the API.
        If no instance is running, tries to get it from file.
        Else creates a new instance and tries to get a token from Deezer API.

        :return:
        """
        Logger.debug("Getting Api instance ...")

        if cls.__INSTANCE is None:
            try:
                Logger.debug("Trying to get Api instance from file ...")
                cls.__INSTANCE = cls.load()
            except IOError:
                Logger.debug("Api instance not saved, trying to get token ...")
                addon = xbmcaddon.Addon('plugin.audio.deezer')
                cls.__INSTANCE = cls(
                    addon.getSetting('username'),
                    addon.getSetting('password')
                )

        return cls.__INSTANCE

    @classmethod
    def clean_cache(cls):
        """Cleans the API cache"""
        Logger.debug("Cleaning API cache ...")
        xbmcvfs.delete(Api.__CACHE_FILE)
        cls.__INSTANCE = None

    def __init__(self, username, password):
        """
        Instantiate a Connection object from username and password.

        :param str username: The user's name
        :param str password: The user's password
        """
        Logger.debug("Creating new API connection ...")
        self._username = username
        self._password = None
        self._access_token = None
        self.set_password(password)
        self._obtain_access_token()

    def __del__(self):
        """Saves the Api instance on disk on deletion"""
        self.save()

    def set_password(self, password):
        """
        Save md5 of user password.

        :param str password: The user's password to save
        """
        md5 = hashlib.md5()
        md5.update(password.encode("utf-8"))
        self._password = md5.hexdigest()

    def save(self):
        """
        Save the connection to a file in kodi special temp folder.
        """
        Logger.debug("Saving Api in '{}'".format(Api.__CACHE_FILE))

        with open(Api.__CACHE_FILE, 'wb') as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load():
        """
        Load a connection from a file in kodi special temp folder.

        :return: an Api object
        """
        Logger.debug("Getting Api from file {}".format(Api.__CACHE_FILE))

        with open(Api.__CACHE_FILE, 'rb') as file:
            cls = pickle.load(file)

        return cls

    def _obtain_access_token(self):
        """
        Obtain access token by pretending to be a smart tv.

        :raise CredentialsException: In case the credentials are empty
        """
        Logger.debug("Connection: Getting access token from API ...")

        if self._username is None or self._password is None:
            raise CredentialsException("Username and password are required!")

        response = requests.get(self._API_AUTH_URL, params={
            'login': self._username,
            'password': self._password,
            'device': 'panasonic'
        }).json()

        Api.check_error(response)

        self._access_token = response['access_token']

    @staticmethod
    def _merge_two_dicts(lhs, rhs):
        """
        Given two dicts, merge them into a new dict as a shallow copy.

        :param dict lhs: First dict
        :param dict rhs: Second dict
        :return: Merged dict
        """
        res = lhs.copy()
        res.update(rhs)
        return res

    def request(self, service, identifiant='', method='', parameters=None):
        """
        Make request to the API and return response as a dict.\n
        Parameters names are the same as described in
        the Deezer API documentation (https://developers.deezer.com/api).

        :param str service:     The service to request
        :param str identifiant:          Item's ID in the service
        :param str method:      Service method
        :param dict parameters: Additional parameters at the end
        :return:                JSON response as dict
        """
        Logger.debug(
            "Requesting {} ...".format('/'.join([str(service), str(identifiant), str(method)]))
        )

        if parameters is None:
            parameters = {}

        url = self._API_BASE_URL.format(service=service, id=identifiant, method=method)
        response = requests.get(url, params=self._merge_two_dicts(
            {'output': 'json', 'access_token': self._access_token},
            parameters
        )).json()

        # if there is a next url, call it
        if 'next' in response:
            response['data'] += Api.request_url(response['next'])['data']

        Api.check_error(response)

        return Api.check_error(response)

    @staticmethod
    def request_url(url):
        """
        Send a GET request to `url`.

        :param str url: Url to query
        :return: JSON response as dict
        """
        Logger.debug("Making custom request ...")

        response = requests.get(url).json()

        # if there is a next url, call it and append data
        if 'next' in response:
            response['data'] += Api.request_url(response['next'])['data']

        Api.check_error(response)

        return response

    def request_streaming(self, identifiant='', st_type='track'):
        """
        Make a request to get the streaming url of `type` with `id`.

        :param str identifiant: ID of the requested item
        :param str st_type: Type of the requested item
        :return: Dict if type is radio or artist, str otherwise
        """
        Logger.info(
            "Connection: Requesting streaming for {} with id {} ...".format(st_type, identifiant)
        )

        if self._access_token is None:
            self._obtain_access_token()

        response = requests.get(self._API_BASE_STREAMING_URL, params={
            'access_token': self._access_token,
            "{}_id".format(st_type): identifiant,
            'device': 'panasonic'
        })

        if st_type.startswith('radio') or st_type.startswith('artist'):
            return response.json()

        return response.text

    @staticmethod
    def check_error(response):
        """
        Checks for errors in every response.
        If errors are found, throws the corresponding exception.

        :param response: The json response to check
        :return: The verified json response
        """
        if 'error' in response:
            ApiExceptionFinder.from_error(response['error'])

        return response
