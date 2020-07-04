# -*- coding: utf-8 -*-

import sys
import urllib
import urlparse

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from resources.lib.DeezerApi import *


my_addon = xbmcaddon.Addon('plugin.audio.deezer')
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

addon = xbmcaddon.Addon()

connection = Connection(addon.getSetting('username'), addon.getSetting('password'))
api = Api(connection)


def build_url(query):
    """
    Build url from `query` dict.
    Used to build url to navigate in menus.

    :param dict query: Options to add in the url
    :return: The encoded url as str
    """
    return base_url + '?' + urllib.urlencode(query)


def main_menu():
    """
    Return main menu items.

    :return: xbmcgui.ListItem list
    """
    items = [
            (build_url({'mode': 'family'}), xbmcgui.ListItem('Family'), True),
            (build_url({'mode': 'user', 'id': 'me'}), xbmcgui.ListItem('Personal'), True),
            (build_url({'mode': 'search-menu'}), xbmcgui.ListItem('Search'), True)
    ]
    return items


def search_menu():
    """
    Return search menu items.

    :return: xbmcgui.ListItem list
    """
    items = [
            (build_url({'mode': 'search', 'filter': ''}), xbmcgui.ListItem('Search all'), True),
            (build_url({'mode': 'search', 'filter': 'album'}), xbmcgui.ListItem('Search albums'), True),
            (build_url({'mode': 'search', 'filter': 'artist'}), xbmcgui.ListItem('Search artists'), True),
            (build_url({'mode': 'search', 'filter': 'track'}), xbmcgui.ListItem('Search tracks'), True)
    ]
    return items


mode = args.get('mode', None)

# display the main menu
if mode is None:
    dir_content = main_menu()
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))
    xbmcplugin.endOfDirectory(addon_handle)


# display a user
elif mode[0] == 'user':
    me = api.get_user(args['id'][0])

    items = []

    for play in me.get_playlists():
        li = xbmcgui.ListItem(play.title)
        url = build_url({'mode': 'playlist', 'id': play.id})

        items.append((url, li, True))

    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.endOfDirectory(addon_handle)


# display family profiles (actually main profile followings since API doesn't give profiles)
elif mode[0] == 'family':
    me = api.get_user('me')

    items = []

    for user in me.get_followings():
        li = xbmcgui.ListItem(user.name)
        url = build_url({'mode': 'user', 'id': user.id})

        items.append((url, li, True))

    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.endOfDirectory(addon_handle)


# display a playlist
elif mode[0] == 'playlist':
    playlist = api.get_playlist(args['id'][0])
    playlist.save()

    items = []

    for track in playlist.get_tracks():
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

        url = build_url({'mode': 'track', 'id': track.id})

        items.append((url, li))

    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)


# when a track is clicked
# add playlist to queue and play selected song
elif mode[0] == 'track':
    current_playlist = Playlist.load()

    xbmc.executebuiltin('Playlist.Clear')
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    startpos = 0

    for pos, track in enumerate(current_playlist.get_tracks()):
        li = xbmcgui.ListItem(track.title)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('music', {
                'duration': track.duration,
                'album': track.get_album().title,
                'artist': track.get_artist().name,
                'title': track.title
        })

        url = build_url({'mode': 'queue_track', 'id': track.id})

        # adding song (as a kodi url) to playlist
        playlist.add(url, li)

        if track.id == int(args['id'][0]):
            startpos = pos

    xbmc.Player().play(playlist, startpos=startpos)


# when a track in queue is selected for playing
elif mode[0] == 'queue_track':
    url = connection.make_request_streaming(args['id'][0], 'track')

    if url.startswith('http'):
        li = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, None)


# display the search menu
elif mode[0] == 'search-menu':
    items = search_menu()
    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.endOfDirectory(addon_handle)
