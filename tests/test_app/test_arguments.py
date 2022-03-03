from app import Arguments
from testcase import TestCase


class TestArguments(TestCase):
    def test_init(self):
        arguments = Arguments(['plugin://plugin.audio.deezer/', 2, ''])

        self.assertEqual('plugin://plugin.audio.deezer/', arguments.base_url)
        self.assertEqual(2, arguments.addon_handle)

    def test_has(self):
        arguments = Arguments(['plugin://plugin.audio.deezer/', 2, '?path=%2Ffamily'])

        self.assertTrue(arguments.has('path'))
        self.assertFalse(arguments.has('p'))

    def test_get(self):
        arguments = Arguments(['plugin://plugin.audio.deezer/', 2, '?path=%2Ffamily'])

        self.assertEqual('/family', arguments.get('path'))

    def test_get_default(self):
        arguments = Arguments(['plugin://plugin.audio.deezer/', 2, '?path=%2Ffamily'])

        self.assertEqual(None, arguments.get('p'))

    def test_get_default_custom(self):
        arguments = Arguments(['plugin://plugin.audio.deezer/', 2, '?path=%2Ffamily'])

        self.assertEqual('foo', arguments.get('p', 'foo'))
