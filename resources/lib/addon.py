# -*- coding: utf8 -*-

# Copyright (C) 2016 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcaddon
import xbmc
import os

ADDON = xbmcaddon.Addon()
ID = ADDON.getAddonInfo('id')
ICON = ADDON.getAddonInfo('icon')
NAME = ADDON.getAddonInfo('name')
PATH = ADDON.getAddonInfo('path').decode("utf-8")
MEDIA_PATH = os.path.join(PATH, "resources", "skins", "Default", "media")
VERSION = ADDON.getAddonInfo('version')
DATA_PATH = xbmc.translatePath("special://profile/addon_data/%s" % ID).decode("utf-8")
