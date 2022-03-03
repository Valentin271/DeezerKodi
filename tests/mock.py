class Mock(object):
    def __init__(self, return_value=None):
        """
        Creates a mock function.

        :param return_value:
        """
        self.calls = 0
        self.args = ()
        self.kwargs = {}
        self.return_value = return_value

    def fn(self, *args, **kwargs):
        """
        Mocked function.

        :param args:
        :param kwargs:
        :return: The value specified to the object.
        """
        self.calls += 1
        self.args = args
        self.kwargs = kwargs

        return self.return_value
