# -*- coding: utf-8 -*-

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


def parse_qs(query):
    """
    Parse a query string into a dict.

    :return: dict
    """
    if query == '':
        return {}

    parsed = {}

    for param in query.split('&'):
        item = param.split('=')
        parsed[item[0]] = item[1]

    return parsed


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
elif MODE == 'user':
    xbmc.log("DeezerKodi: Mode 'user'", xbmc.LOGINFO)
    me = API.get_user(ARGS['id'])
    me.display()


# display family profiles (actually main profile's followings since API doesn't give profiles)
elif MODE == 'family':
    xbmc.log("DeezerKodi: Mode 'family'", xbmc.LOGINFO)
    me = API.get_user('me')
    me.display_family_profiles()


# display a playlist
elif MODE == 'playlist':
    xbmc.log("DeezerKodi: Mode 'playlist'", xbmc.LOGINFO)
    playlist = API.get_playlist(ARGS['id'])
    playlist.display()


# when a track is clicked
# add playlist to queue and play selected song
elif MODE == 'track':
    xbmc.log("DeezerKodi: Mode 'track'", xbmc.LOGINFO)
    if ARGS['container'][0] == 'playlist':
        current_list = Playlist.load()
    else:
        current_list = Album.load()

    current_list.queue(ARGS['id'])


# when a track in queue is selected for playing
elif MODE == 'queue_track':
    xbmc.log("DeezerKodi: Mode 'queue_track'", xbmc.LOGINFO)
    url = CONNECTION.make_request_streaming(ARGS['id'], 'track')

    if url.startswith('http'):
        xbmc.log("Playing track " + ARGS['id'], xbmc.LOGDEBUG)
        li = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    else:
        xbmc.log("Unplayable track " + ARGS['id'], xbmc.LOGWARNING)
        xbmcgui.Dialog().notification(
            "Unplayable track",
            "Track " + ARGS['id'] + " cannot be played.",
            xbmcgui.NOTIFICATION_WARNING,
            sound=False
        )
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())


# display the search menu
elif MODE == 'search-menu':
    xbmc.log("DeezerKodi: Mode 'search-menu'", xbmc.LOGINFO)
    items = search_menu()
    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.endOfDirectory(addon_handle)


# when the user wants to search for something
elif MODE == 'search':
    xbmc.log("DeezerKodi: Mode 'search'", xbmc.LOGINFO)

    query = xbmcgui.Dialog().input('Search')

    # if user canceled
    if query != '':
        result = API.search(query, ARGS['filt'])
        result.display()


# play a single track from a search
elif MODE == 'searched_track':
    xbmc.log("DeezerKodi: Mode 'searched_track'", xbmc.LOGINFO)
    track = API.get_track(ARGS['id'])
    track.play()


# displays an album
elif MODE == 'album':
    xbmc.log("DeezerKodi: Mode 'album'", xbmc.LOGINFO)
    album = API.get_album(ARGS['id'])
    album.display()


# displays an artist
elif MODE == 'artist':
    xbmc.log("DeezerKodi: Mode 'artist'", xbmc.LOGINFO)
    artist = API.get_artist(ARGS['id'])
    artist.display()

# Saving connection with token for next time
CONNECTION.save()
xbmc.log('DeezerKodi: End of addon execution', xbmc.LOGINFO)
