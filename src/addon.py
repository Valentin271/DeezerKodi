# -*- coding: utf-8 -*-

import sys
import urlparse

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from resources.lib.DeezerApi import *


my_addon = xbmcaddon.Addon('plugin.audio.deezer')
args = urlparse.parse_qs(sys.argv[2][1:])

addon = xbmcaddon.Addon()

connection = Connection(addon.getSetting('username'), addon.getSetting('password'))
api = Api(connection)


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
            (build_url({'mode': 'search', 'filt': 'track'}), xbmcgui.ListItem('Search tracks'), True),
            # (build_url({'mode': 'search', 'filt': 'album'}), xbmcgui.ListItem('Search albums'), True),
            # (build_url({'mode': 'search', 'filt': 'artist'}), xbmcgui.ListItem('Search artists'), True)
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
    me.display()


# display family profiles (actually main profile followings since API doesn't give profiles)
elif mode[0] == 'family':
    me = api.get_user('me')
    me.display_family_profiles()


# display a playlist
elif mode[0] == 'playlist':
    playlist = api.get_playlist(args['id'][0])
    playlist.display()


# when a track is clicked
# add playlist to queue and play selected song
elif mode[0] == 'track':
    if args['container'][0] == 'playlist':
        current_list = Playlist.load()
    else:
        current_list = Album.load()

    current_list.queue(args['id'][0])


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


# when the user wants to search for something
elif mode[0] == 'search':
    query = xbmcgui.Dialog().input('Search')
    result = api.search(query, args['filt'][0])

    result.display()


# play a single track from a search
elif mode[0] == 'searched_track':
    track = api.get_track(args['id'][0])
    track.play()