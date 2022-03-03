class BaseActions(object):
    """Base class for defining actions"""

    args = None
    """Application's arguments"""

    @classmethod
    def index(cls):
        """
        Gets the index of a resource.

        :return: list, tuple or ListView
        """

    @classmethod
    def show(cls, identifiant):
        """
        Shows a resource.

        :param identifiant: Resource's ID
        :return: list, tuple or ListView
        """
