# -*- coding: utf-8 -*-

try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.DeezerApi import Connection, Api, build_url, addon_handle, Playlist, Album
from resources.lib.deezer_exception import QuotaException

# Initializing addon
ADDON = xbmcaddon.Addon('plugin.audio.deezer')

VERSION = ADDON.getAddonInfo('version')
xbmc.log("DeezerKodi: Starting DeezerKodi " + VERSION, xbmc.LOGINFO)

ARGS = parse_qs(sys.argv[2][1:])

CONNECTION = None
# Trying to get token from file
try:
    CONNECTION = Connection.load()
except IOError:
    xbmc.log("DeezerKodi: Failed to get token from file, trying API request instead", xbmc.LOGWARNING)

    # If file does not exist, try to get token from API
    try:
        # If no credentials, open setting window
        if ADDON.getSetting('username') == '' or ADDON.getSetting('password') == '':
            ADDON.openSettings()

        CONNECTION = Connection(ADDON.getSetting('username'), ADDON.getSetting('password'))

    except QuotaException:
        xbmc.log("DeezerKodi: Cannot get token from API", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Error", "Quota limit exceeded, please wait and retry.")
        exit()

API = Api(CONNECTION)


def main_menu():
    """
    Return main menu items.

    :return: xbmcgui.ListItem list
    """
    xbmc.log('DeezerKodi: Getting main menu content', xbmc.LOGDEBUG)
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
    xbmc.log('DeezerKodi: Getting search menu content', xbmc.LOGDEBUG)
    items = [
        (build_url({'mode': 'search', 'filt': 'track'}), xbmcgui.ListItem('Search tracks'), True),
        (build_url({'mode': 'search', 'filt': 'album'}), xbmcgui.ListItem('Search albums'), True),
        (build_url({'mode': 'search', 'filt': 'artist'}), xbmcgui.ListItem('Search artists'), True)
    ]
    return items


MODE = ARGS.get('mode', None)

# display the main menu
if MODE is None:
    xbmc.log("DeezerKodi: Mode 'None'", xbmc.LOGINFO)
    dir_content = main_menu()
    xbmc.log('DeezerKodi: Displaying main menu', xbmc.LOGDEBUG)
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))
    xbmcplugin.endOfDirectory(addon_handle)


# display a user
elif MODE[0] == 'user':
    xbmc.log("DeezerKodi: Mode 'user'", xbmc.LOGINFO)
    me = API.get_user(ARGS['id'][0])
    me.display()


# display family profiles (actually main profile's followings since API doesn't give profiles)
elif MODE[0] == 'family':
    xbmc.log("DeezerKodi: Mode 'family'", xbmc.LOGINFO)
    me = API.get_user('me')
    me.display_family_profiles()


# display a playlist
elif MODE[0] == 'playlist':
    xbmc.log("DeezerKodi: Mode 'playlist'", xbmc.LOGINFO)
    playlist = API.get_playlist(ARGS['id'][0])
    playlist.display()


# when a track is clicked
# add playlist to queue and play selected song
elif MODE[0] == 'track':
    xbmc.log("DeezerKodi: Mode 'track'", xbmc.LOGINFO)
    if ARGS['container'][0] == 'playlist':
        current_list = Playlist.load()
    else:
        current_list = Album.load()

    current_list.queue(ARGS['id'][0])


# when a track in queue is selected for playing
elif MODE[0] == 'queue_track':
    xbmc.log("DeezerKodi: Mode 'queue_track'", xbmc.LOGINFO)
    url = CONNECTION.make_request_streaming(ARGS['id'][0], 'track')

    if url.startswith('http'):
        li = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, None)


# display the search menu
elif MODE[0] == 'search-menu':
    xbmc.log("DeezerKodi: Mode 'search-menu'", xbmc.LOGINFO)
    items = search_menu()
    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.endOfDirectory(addon_handle)


# when the user wants to search for something
elif MODE[0] == 'search':
    xbmc.log("DeezerKodi: Mode 'search'", xbmc.LOGINFO)
    query = xbmcgui.Dialog().input('Search')
    result = API.search(query, ARGS['filt'][0])

    result.display()


# play a single track from a search
elif MODE[0] == 'searched_track':
    xbmc.log("DeezerKodi: Mode 'searched_track'", xbmc.LOGINFO)
    track = API.get_track(ARGS['id'][0])
    track.play()


# displays an album
elif MODE[0] == 'album':
    xbmc.log("DeezerKodi: Mode 'album'", xbmc.LOGINFO)
    album = API.get_album(ARGS['id'][0])
    album.display()


# displays an artist
elif MODE[0] == 'artist':
    xbmc.log("DeezerKodi: Mode 'artist'", xbmc.LOGINFO)
    artist = API.get_artist(ARGS['id'][0])
    artist.display()

# Saving connection with token for next time
CONNECTION.save()
xbmc.log('DeezerKodi: End of addon execution', xbmc.LOGINFO)
