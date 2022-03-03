from lib.exceptions import QuotaException, ApiExceptionFinder, ApiException
from testcase import TestCase


class TestApiExceptionFinder(TestCase):
    def test_from_error(self):
        self.assertRaises(
            QuotaException,
            ApiExceptionFinder.from_error,
            {'code': 4, 'message': 'foo bar', 'type': 'Exception'}
        )

    def test_from_error_unknown_code(self):
        self.assertRaises(
            ApiException,
            ApiExceptionFinder.from_error,
            {'code': 0, 'message': 'foo bar', 'type': 'Exception'}
        )
