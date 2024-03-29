import xbmcaddon


class Settings:
    """Simple wrapper around kodi settings"""

    addon = xbmcaddon.Addon('plugin.audio.deezer')

    @classmethod
    def get(cls, identifiant: str) -> str:
        """
        Get value associated with `identifiant`
        :param str identifiant: Setting id
        """
        return cls.addon.getSetting(identifiant)

    @classmethod
    def get_bool(cls, identifiant: str) -> bool:
        """
        Get value associated with `identifiant` as a boolean
        :param str identifiant: Setting id
        """
        return cls.addon.getSettingBool(identifiant)

    @classmethod
    def get_int(cls, identifiant: str) -> int:
        """
        Get value associated with `identifiant` as an int
        :param str identifiant: Setting id
        """
        return cls.addon.getSettingInt(identifiant)

    @classmethod
    def get_float(cls, identifiant: str) -> float:
        """
        Get value associated with `identifiant` as a float
        :param str identifiant: Setting id
        """
        return cls.addon.getSettingNumber(identifiant)
