import unittest


class TestCase(unittest.TestCase):
    def assertCalled(self, mock):
        """
        Assert that mock have been called at leat one time.

        :param mock.Mock mock: mock to test
        """
        self.assertGreaterEqual(mock.calls, 1)

    def assertCalledOnce(self, mock):
        """
        Assert mock have been called exactly one time.

        :param mock.Mock mock: mock to test
        """
        self.assertEqual(1, mock.calls)

    def assertCalledTimes(self, mock, n):
        """
        Assert mock have been called exactly `n` time.

        :param mock.Mock mock: mock to test
        :param int n: number of calls
        """
        self.assertEqual(n, mock.calls)

    def assertCalledWith(self, mock, *args, **kwargs):
        """
        Assert that a mock have been called with certain parameters

        :param mock.Mock mock: mock to test
        :param args:
        :param kwargs:
        """
        self.assertTupleEqual(args, mock.args)
        self.assertDictEqual(kwargs, mock.kwargs)

    def assertNotCalled(self, mock):
        """
        Assert that mock has not been called.

        :param mock.Mock mock: mock to test
        """
        self.assertEqual(0, mock.calls)
