# -*- coding: utf-8 -*-

import sys
import urllib
import urlparse
import time
import logging

import sqlite3

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

import resources.lib.DeezerApi as dzapi

# initial time, used to determine the time the program took to execute
ti = time.time()

my_addon = xbmcaddon.Addon('plugin.audio.deezer')
addon_path = my_addon.getAddonInfo('path')  # path to the addon
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

# setting up logfile
logfile_path = xbmc.translatePath('special://logpath/deezer.log')
log_format = '%(asctime)s %(levelname)8s:  %(message)s'
logging.basicConfig(filename=logfile_path, format=log_format, datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

xbmcplugin.setContent(addon_handle, 'songs')
addon = xbmcaddon.Addon()

connection = dzapi.Connection(addon.getSetting('username'), addon.getSetting('password'))


def build_url(query):
    """Used to build url to navigate in menus"""
    return base_url + '?' + urllib.urlencode(query)


def main_menu():
    """Show the main menu listing"""
    logging.info('Listing main menu ...')
    items = [
        (build_url({'mode': 'folder', 'foldername': 'Family'}), xbmcgui.ListItem('Family'), True),
        (build_url({'mode': 'folder', 'foldername': 'Personal'}), xbmcgui.ListItem('Personal'), True),
        (build_url({'mode': 'search'}), xbmcgui.ListItem('Search'), True)
    ]
    return items


def family():
    """
    Show profile of family account. The api doesn't allow that so we have to query
    the main account followings (profiles follows the main account by default).
    """
    items = []

    logging.info('Querying family profiles ...')
    data = connection.make_request('user', 'me', 'followings')

    logging.debug('Listing family profiles ...')
    for user in data['data']:
        url = build_url({'mode': 'user', 'username': user['name'], 'user_id': user['id']})
        li = xbmcgui.ListItem(user['name'], iconImage='DefaultUser.png')
        items.append((url, li, True))

    return items


def play_list(played_id):
    """Add playlist in queue and play the selected song"""
    logging.debug('Playlist cleared')
    xbmc.executebuiltin('Playlist.Clear')
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    track_offset = 0  # the offset of the selected track

    # connecting to DB
    logging.debug('Openning playlist DB')
    playlist_tmpdb_conn = sqlite3.connect(xbmc.translatePath('special://temp/deezer-playlist.tmpdb'))
    playlist_tmpdb = playlist_tmpdb_conn.cursor()

    # gathering DB data
    logging.info('Querying DB for songs info')
    playlist_tmpdb.execute('SELECT * FROM playlist')
    lines = playlist_tmpdb.fetchall()

    for pos, line in enumerate(lines):
        id, name, album, image_big, artist, duration = line

        # setting song infos (seems to work only with kodi 18)
        li = xbmcgui.ListItem(name, thumbnailImage=image_big)
        li.setInfo('music', {'title': name, 'album': album, 'artist': artist, 'duration': duration})

        # adding song (as a kodi url) to playlist
        playlist.add(build_url({'mode': 'track', 'trackid': id}), li)

        # if the current id match the selected song, mark the playlist offset to play it later
        if int(id) == int(played_id):
            track_offset = pos

    playlist_tmpdb_conn.close()
    logging.info('Starting playlist at offset %s', str(track_offset))
    xbmc.Player().play(playlist, startpos=track_offset)


def play_track(id):
    """
    Request a streaming url and play the song. Also check the validity of the url
    (this function is used when playing the next song in queue)
    """
    logging.debug('Getting streaming url for track %s', id)
    url = connection.make_request_streaming_custom(id, 'track')

    if url.startswith('http'):
        logging.debug('Got valid url, starting playback')
        li = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)
    else:
        logging.warning('Got non-valid url, passing track')
        xbmcplugin.setResolvedUrl(addon_handle, False, None)


def show_user(id):
    """Show the "content" of a user, the playlists"""
    items = []
    logging.info('Querying user\'s playlists')
    data = connection.make_request('user', id, 'playlists')

    logging.debug('Listing user\'s playlists')
    for playli in data['data']:
        url = build_url({'mode': 'playlist', 'playlist_id': playli['id']})

        li = xbmcgui.ListItem(playli['title'])
        li.setArt({'thumb': playli['picture_big'], 'icon': playli['picture_small'], 'fanart': playli['picture_xl']})

        items.append((url, li, True))

    return items


def show_playlist(playlist_data, reverse=True, album_infos={}):
    """
    Gather playlist content, display it
    and write it in a tmp DB for queue adding later.
    album_infos: dict like {'name': album_name, 'cover': album_cover} # used when displaying album
    """
    items = []
    playlist = []

    if album_infos:
        album_name = album_infos['name']
        album_cover = album_infos['cover']

    # connecting to DB
    logging.debug('Opening playlist DB')
    playlist_tmpdb_conn = sqlite3.connect(xbmc.translatePath('special://temp/deezer-playlist.tmpdb'))
    playlist_tmpdb = playlist_tmpdb_conn.cursor()

    # creating DB or clearing from previous playlist
    playlist_tmpdb.execute('DROP TABLE IF EXISTS playlist')
    playlist_tmpdb.execute('CREATE TABLE IF NOT EXISTS playlist (id int, name text, album text, image_big text, artist text, duration int)')

    logging.info('Gathering playlist info ...')
    while True:
        for track in playlist_data['data']:
            # album listing from api does not include album infos
            if not album_infos:
                album_name = track['album']['title']
                # sometimes tracks doesn't have cover
                try:
                    album_cover = track['album']['cover_big']
                except KeyError:
                    album_cover = None

            li = xbmcgui.ListItem(track['title'], iconImage=album_cover)
            li.setInfo('music', {'album': album_name, 'artist': track['artist']['name'], 'duration': track['duration']})
            url = build_url({'mode': 'list', 'trackid': track['id']})
            items.append((url, li))
            playlist.append((str(track['id']), track['title'], album_name, album_cover, track['artist']['name'], track['duration']))

        # if there is no part left to the playlist break the loop
        try:
            playlist_data = connection.make_request_url(playlist_data['next'])
        except KeyError:
            logging.info('Playlist gathering done')
            break

    # reverse so the last track added is first in the gui
    if reverse:
        items.reverse()
        playlist.reverse()

    logging.debug('Adding songs entries to playlist DB')
    playlist_tmpdb.executemany('INSERT INTO playlist VALUES (?,?,?,?,?,?)', playlist)
    playlist_tmpdb_conn.commit()
    playlist_tmpdb_conn.close()
    logging.debug('Closed playlist DB')

    return items


def show_search():
    """Show the different search mode"""
    logging.debug('Listing search modes')
    items = [
        (build_url({'mode': 'track_search'}), xbmcgui.ListItem('Search track'), True),
        (build_url({'mode': 'artist_search'}), xbmcgui.ListItem('Search artist'), True),
        (build_url({'mode': 'album_search'}), xbmcgui.ListItem('Search album'), True)
    ]
    return items


def show_artist_search():
    """Show results of a search for an artist"""
    items = []

    # asking search string
    logging.info('Requesting artist search results')
    query = xbmcgui.Dialog().input('Search artist')
    data = connection.make_request('search', method='artist', parameters={'q': query})

    logging.debug('Listing artist search results')
    for artist in data['data']:
        li = xbmcgui.ListItem(artist['name'], iconImage=artist['picture_big'])
        url = build_url({'mode': 'artist', 'artist_id': artist['id']})
        items.append((url, li, True))

    return items


def show_album_search():
    """Show results of a search about an album"""
    items = []

    # asking search string
    logging.info('Requesting album search results')
    query = xbmcgui.Dialog().input('Search album')
    data = connection.make_request('search', method='album', parameters={'q': query})

    logging.debug('Listing album search results')
    for album in data['data']:
        url = build_url({'mode': 'album',
                         'album_id': album['id'],
                         'album_name': album['title'].encode('utf-8', 'backslashreplace'),
                         'album_cover': album['cover_big'].encode('utf-8', 'backslashreplace')})
        li = xbmcgui.ListItem(album['title'])
        li.setArt({'icon': album['cover_big'], 'fanart': album['cover_xl']})
        items.append((url, li, True))

    return items


def show_track_search():
    """Show results for a track search"""
    items = []

    # asking search string
    logging.info('Requesting tracks search results')
    query = xbmcgui.Dialog().input('Search track')
    data = connection.make_request('search', method='track', parameters={'q': query})

    logging.debug('Listing tracks search results')
    items = show_playlist(data, reverse=False)
    # for track in data['data']:
    #     try:
    #         icon = track['album']['cover_big']
    #         fanart = track['album']['cover_xl']
    #     except KeyError:
    #         icon = fanart = None
    #     with open(logfile_path, 'a') as file:
    #         file.write(str(track['id']) + '\n')
    #     url = build_url({'mode': 'list', 'trackid': track['id']})
    #     li = xbmcgui.ListItem(track['title'])
    #     li.setInfo('music', {'artist': track['artist']['name'], 'album': track['album']['title'], 'duration': track['duration']})
    #     li.setArt({'icon': icon, 'fanart': fanart})
    #     items.append((url, li))

    return items


def show_artist(id):
    """Show artist's "content": albums, songs, top"""
    logging.debug('Listing artist\'s content')
    items = [
        (build_url({'mode': 'artist-top', 'artist_id': id}), xbmcgui.ListItem('Top'), True),
        (build_url({'mode': 'artist-albums', 'artist_id': id}), xbmcgui.ListItem('Albums'), True)
    ]
    return items


def show_albums(album_list):
    """Show a list of album"""
    logging.debug('Listing albums')
    items = []

    while True:
        for album in album_list['data']:
            url = build_url({'mode': 'album',
                             'album_id': album['id'],
                             'album_name': album['title'].encode('utf-8', 'backslashreplace'),
                             'album_cover': album['cover_big'].encode('utf-8', 'backslashreplace')})
            li = xbmcgui.ListItem(album['title'])
            li.setArt({'icon': album['cover_big'], 'fanart': album['cover_xl']})
            items.append((url, li, True))

        try:
            album_list = connection.make_request_url(album_list['next'])
        except KeyError:
            logging.debug('End of album listing')
            break

    return items


mode = args.get('mode', None)

if mode is None:
    dir_content = main_menu()
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'folder':
    if args['foldername'][0] == 'Personal':
        dir_content = personal()
        xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))
    elif args['foldername'][0] == 'Family':
        dir_content = family()
        xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'list':
    play_list(args['trackid'][0])

elif mode[0] == 'track':
    play_track(args['trackid'][0])

elif mode[0] == 'user':
    dir_content = show_user(args['user_id'][0])
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'playlist':
    data = connection.make_request('playlist', args['playlist_id'][0], 'tracks')
    dir_content = show_playlist(data)
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'search':
    dir_content = show_search()
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'track_search':
    dir_content = show_track_search()
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'artist_search':
    dir_content = show_artist_search()
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'album_search':
    dir_content = show_album_search()
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'artist':
    dir_content = show_artist(args['artist_id'][0])
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'artist-top':
    top_url = connection.make_request('artist', args['artist_id'][0])
    data = connection.make_request_url(top_url['tracklist'])
    dir_content = show_playlist(data, reverse=False)
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'artist-albums':
    data = connection.make_request('artist', args['artist_id'][0], 'albums')
    dir_content = show_albums(data)
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

elif mode[0] == 'album':
    data = connection.make_request('album', args['album_id'][0], 'tracks')
    dir_content = show_playlist(data, reverse=False, album_infos={'name': args['album_name'][0], 'cover': args['album_cover'][0]})
    xbmcplugin.addDirectoryItems(addon_handle, dir_content, len(dir_content))

xbmcplugin.endOfDirectory(addon_handle)

# time ended
te = time.time()
logging.info('Total process took %ss\n', str(te-ti))
