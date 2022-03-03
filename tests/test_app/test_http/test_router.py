from app import Arguments
from mock import Mock
from src.app.http import Router
from testcase import TestCase


class TestRouter(TestCase):
    args = Arguments(['plugin://plugin.audio.deezer/', 2, ''])

    def test_add(self):
        mock = Mock()
        router = Router("/")

        router.route(TestRouter.args)
        self.assertEqual(0, mock.calls)

        router.add('/', mock.fn)

        router.route(TestRouter.args)
        self.assertCalledOnce(mock)

    def test_route(self):
        mock_a = Mock()
        mock_b = Mock()

        router = Router("/")
        router.add("/personal", mock_b.fn)
        router.add("/", mock_a.fn)

        router.route(TestRouter.args)
        self.assertCalledOnce(mock_a)
        self.assertNotCalled(mock_b)

    def test_route_return(self):
        mock_a = Mock('a')
        mock_b = Mock('b')

        router = Router("/")
        router.add("/personal", mock_b.fn)
        router.add("/", mock_a.fn)

        self.assertEqual('a', router.route(TestRouter.args))

    def test_route_two_deep(self):
        mock_a = Mock()
        mock_b = Mock()

        router = Router("/personal/playlists")
        router.add("/", mock_b.fn)
        router.add("/personal/playlists", mock_a.fn)

        router.route(TestRouter.args)
        self.assertCalledOnce(mock_a)
        self.assertNotCalled(mock_b)

    def test_route_similar(self):
        mock_a = Mock()
        mock_b = Mock()

        router = Router("/personal/playlists")
        router.add("/personal", mock_b.fn)
        router.add("/personal/playlists", mock_a.fn)

        router.route(TestRouter.args)
        self.assertCalledOnce(mock_a)
        self.assertNotCalled(mock_b)

    def test_route_with_parameter(self):
        mock_a = Mock()
        mock_b = Mock()

        router = Router("/playlists/10")
        router.add("/family", mock_b.fn)
        router.add("/playlists/{identifiant}", mock_a.fn)

        router.route(TestRouter.args)
        self.assertCalledOnce(mock_a)
        self.assertCalledWith(mock_a, identifiant="10")
        self.assertNotCalled(mock_b)

    def test_route_with_two_parameters(self):
        mock_a = Mock()
        mock_b = Mock()

        router = Router("/playlists/10/track/2")
        router.add("/family", mock_b.fn)
        router.add("/playlists/{identifiant}/track/{id_track}", mock_a.fn)

        router.route(TestRouter.args)
        self.assertCalledOnce(mock_a)
        self.assertCalledWith(mock_a, identifiant="10", id_track="2")
        self.assertNotCalled(mock_b)
