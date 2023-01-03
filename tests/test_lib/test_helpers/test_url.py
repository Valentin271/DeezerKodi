from urllib.parse import unquote

from lib.helpers.url import build, concat
from testcase import TestCase


class TestBuild(TestCase):
    def test_empty(self):
        self.assertEqual(build({}), '')

    def test_one(self):
        url = build({'path': '/family'})
        self.assertEqual('path=/family', unquote(url))

    def test_two(self):
        url = build({'path': '/family', 'q': 'e'})
        self.assertIn(unquote(url), ['path=/family&q=e', 'q=e&path=/family'])


class TestConcat(TestCase):
    def test_simple(self):
        self.assertEqual(concat(), '/')

    def test_one(self):
        self.assertEqual(concat('family'), '/family')

    def test_two(self):
        self.assertEqual(concat('family', '1'), '/family/1')

    def test_with_int(self):
        self.assertEqual(concat('family', 1), '/family/1')

    def test_slashes(self):
        self.assertEqual(concat('/family/'), '/family')

    def test_two_with_slashes(self):
        self.assertEqual(concat('/family/', '/1/'), '/family/1')
