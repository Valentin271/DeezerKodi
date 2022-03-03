import xbmcgui

from app.views.base_view import BaseView
from testcase import TestCase


class TestBaseView(TestCase):
    def test_set_icon(self):
        item = BaseView({'path': '/foo/bar'}, 'Test', True)
        chain = item.set_icon('/icon.png')

        self.assertIsInstance(chain, BaseView)

    def test_view(self):
        item = BaseView({'path': '/foo/bar'}, 'Test', True)
        view = item.view('plugin://plugin.audio.deezer/')

        self.assertEqual('plugin://plugin.audio.deezer/?path=%2ffoo%2fbar', view[0].lower())
        self.assertIsInstance(view[1], xbmcgui.ListItem)
        self.assertTrue(view[2])
