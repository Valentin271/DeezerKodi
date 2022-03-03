import xbmcgui

from lib.helpers import url


class BaseView(object):
    """Defines a viewable item in Kodi."""

    def __init__(self, options, label, is_dir):
        """
        Initialize a Base view which can be displayed.

        :param dict options: Options to give to this item
        :param str label: Displayed label
        :param bool is_dir: This item is a directory
        """
        self.__url = url.build(options)
        self._item = xbmcgui.ListItem(label)
        self.__is_dir = is_dir

    def set_icon(self, path):
        """
        Sets this view's icon

        :param str path: icon's full path
        :return: self, to chain
        """
        self._item.setArt({
            'icon': path
        })

        return self

    def view(self, base_url):
        """
        Returns an item that can be displayed by Kodi.

        :param str base_url: The base url that reference this addon.
        :return: An item that can be displayed by Kodi
        """
        return base_url + '?' + self.__url, self._item, self.__is_dir
