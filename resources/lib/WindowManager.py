# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details
from Utils import *
import xbmcaddon
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")


class WindowManager():
    window_stack = []

    def __init__(self):
        pass

    def add_to_stack(self, window):
        """
        add window / dialog to global window stack
        """
        self.window_stack.append(window)

    def pop_stack(self):
        """
        get newest item from global window stack
        """
        if self.window_stack:
            dialog = self.window_stack.pop()
            dialog.doModal()

    def open_movie_info(self, prev_window=None, movie_id=None, dbid=None, name=None, imdb_id=None):
        """
       open movie info, deal with window stack
        """
        import DialogVideoInfo
        dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=movie_id, dbid=dbid, name=name, imdb_id=imdb_id)
        if dialog.data:
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()

    def open_tvshow_info(self, prev_window=None, tvshow_id=None, dbid=None, tvdb_id=None, imdb_id=None, name=None):
        """
       open tvshow info, deal with window stack
        """
        import DialogTVShowInfo
        dialog = DialogTVShowInfo.DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=tvshow_id, dbid=dbid, tvdb_id=tvdb_id, imdb_id=imdb_id, name=name)
        if dialog.data:
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()

    def open_season_info(self, prev_window=None, tvshow_id=None, season=None, tvshow=None):
        """
       open season info, deal with window stack
       needs *season + (*tvshow_id OR *tvshow)
        """
        import DialogSeasonInfo
        dialog = DialogSeasonInfo.DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=tvshow_id, season=season, tvshow=tvshow)
        if dialog.data:
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()

    def open_actor_info(self, prev_window=None, actor_id=None, name=None):
        """
       open actor info, deal with window stack
        """
        import DialogActorInfo
        dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, name=name)
        if dialog.data:
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()



wm = WindowManager()
