"""
The routes file defines the routes availables in the application.
"""
from app.actions import \
    HomeActions, \
    FamilyActions, \
    PersonalActions, \
    PlaylistsActions, \
    AlbumsActions, \
    ArtistsActions, \
    SearchActions, \
    TracksActions


def load(router):
    """
    Loads the app routes into the router.

    :param app.http.router.Router router:
    """
    router.add("/", HomeActions.index)

    router.add("/family", FamilyActions.index)
    router.add("/family/{identifiant}", FamilyActions.show)
    router.add("/family/{identifiant}/playlists", FamilyActions.playlists)
    router.add("/family/{identifiant}/albums", FamilyActions.albums)
    router.add("/family/{identifiant}/artists", FamilyActions.artists)
    router.add("/family/{identifiant}/flow", FamilyActions.flow)

    router.add("/personal", PersonalActions.index)
    router.add("/personal/playlists", PersonalActions.playlists)
    router.add("/personal/albums", PersonalActions.albums)
    router.add("/personal/artists", PersonalActions.artists)
    router.add("/personal/flow", PersonalActions.flow)

    router.add("/playlists/{identifiant}", PlaylistsActions.show)
    router.add("/albums/{identifiant}", AlbumsActions.show)
    router.add("/tracks/{identifiant}/play", TracksActions.play)

    router.add("/artists/{identifiant}", ArtistsActions.show)
    router.add("/artists/{identifiant}/top", ArtistsActions.top)
    router.add("/artists/{identifiant}/albums", ArtistsActions.albums)

    router.add("/search", SearchActions.index)
    router.add("/search/tracks", SearchActions.tracks)
    router.add("/search/albums", SearchActions.albums)
    router.add("/search/artists", SearchActions.artists)
