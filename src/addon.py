# -*- coding: utf-8 -*-
"""
Entry point of this kodi addon.
"""

import sys

from app import Application, Arguments

ARGS = Arguments(sys.argv)

APP = Application(ARGS)
APP.run()
