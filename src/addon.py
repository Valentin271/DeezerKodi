# -*- coding: utf-8 -*-

import urlparse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from resources.lib.DeezerApi import Connection, Api, build_url, addon_handle, Playlist, Album
from resources.lib.deezer_exception import QuotaException


# Initializing addon
addon = xbmcaddon.Addon('plugin.audio.deezer')
args = urlparse.parse_qs(sys.argv[2][1:])


connection = None
# Trying to get token from file
try:
    connection = Connection.load()
except IOError:
    xbmc.log("DeezerKodi: Failed to get token from file, trying API request instead", xbmc.LOGWARNING)

    # If file does not exist, try to get token from API
    try:
        connection = Connection(addon.getSetting('username'), addon.getSetting('password'))
    except QuotaException:
        xbmc.log("DeezerKodi: Cannot get token from API", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Error", "Quota limit exceeded, please wait and retry.")
        exit()

api = Api(connection)


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


mode = args.get('mode', None)

# display the main menu
if mode is None:
    xbmc.log("DeezerKodi: Mode 'None'", xbmc.LOGINFO)
    dir_content = main_menu()
    xbmc.log('DeezerKodi: Displaying main menu', xbmc.LOGDEBUG)
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))
    xbmcplugin.endOfDirectory(addon_handle)


# display a user
elif mode[0] == 'user':
    xbmc.log("DeezerKodi: Mode 'user'", xbmc.LOGINFO)
    me = api.get_user(args['id'][0])
    me.display()


# display family profiles (actually main profile's followings since API doesn't give profiles)
elif mode[0] == 'family':
    xbmc.log("DeezerKodi: Mode 'family'", xbmc.LOGINFO)
    me = api.get_user('me')
    me.display_family_profiles()


# display a playlist
elif mode[0] == 'playlist':
    xbmc.log("DeezerKodi: Mode 'playlist'", xbmc.LOGINFO)
    playlist = api.get_playlist(args['id'][0])
    playlist.display()


# when a track is clicked
# add playlist to queue and play selected song
elif mode[0] == 'track':
    xbmc.log("DeezerKodi: Mode 'track'", xbmc.LOGINFO)
    if args['container'][0] == 'playlist':
        current_list = Playlist.load()
    else:
        current_list = Album.load()

    current_list.queue(args['id'][0])


# when a track in queue is selected for playing
elif mode[0] == 'queue_track':
    xbmc.log("DeezerKodi: Mode 'queue_track'", xbmc.LOGINFO)
    url = connection.make_request_streaming(args['id'][0], 'track')

    if url.startswith('http'):
        li = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    else:
        xbmcplugin.setResolvedUrl(addon_handle, False, None)


# display the search menu
elif mode[0] == 'search-menu':
    xbmc.log("DeezerKodi: Mode 'search-menu'", xbmc.LOGINFO)
    items = search_menu()
    xbmcplugin.addDirectoryItems(addon_handle, items, len(items))
    xbmcplugin.endOfDirectory(addon_handle)


# when the user wants to search for something
elif mode[0] == 'search':
    xbmc.log("DeezerKodi: Mode 'search'", xbmc.LOGINFO)
    query = xbmcgui.Dialog().input('Search')
    result = api.search(query, args['filt'][0])

    result.display()


# play a single track from a search
elif mode[0] == 'searched_track':
    xbmc.log("DeezerKodi: Mode 'searched_track'", xbmc.LOGINFO)
    track = api.get_track(args['id'][0])
    track.play()


# displays an album
elif mode[0] == 'album':
    xbmc.log("DeezerKodi: Mode 'album'", xbmc.LOGINFO)
    album = api.get_album(args['id'][0])
    album.display()


# displays an artist
elif mode[0] == 'artist':
    xbmc.log("DeezerKodi: Mode 'artist'", xbmc.LOGINFO)
    artist = api.get_artist(args['id'][0])
    artist.display()

# Saving connection with token for next time
connection.save()
