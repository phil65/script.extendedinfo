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


class WindowManager(object):
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
        self.open_dialog(dialog, prev_window)

    def open_tvshow_info(self, prev_window=None, tvshow_id=None, dbid=None, tvdb_id=None, imdb_id=None, name=None):
        """
       open tvshow info, deal with window stack
        """
        import DialogTVShowInfo
        dialog = DialogTVShowInfo.DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=tvshow_id, dbid=dbid, tvdb_id=tvdb_id, imdb_id=imdb_id, name=name)
        self.open_dialog(dialog, prev_window)

    def open_season_info(self, prev_window=None, tvshow_id=None, season=None, tvshow=None):
        """
       open season info, deal with window stack
       needs *season AND (*tvshow_id OR *tvshow)
        """
        import DialogSeasonInfo
        dialog = DialogSeasonInfo.DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=tvshow_id, season=season, tvshow=tvshow)
        self.open_dialog(dialog, prev_window)

    def open_episode_info(self, prev_window=None, tvshow_id=None, season=None, episode=None):
        """
       open season info, deal with window stack
       needs *tvshow_id AND *season AND *episode
        """
        import DialogEpisodeInfo
        dialog = DialogEpisodeInfo.DialogEpisodeInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, show_id=tvshow_id, season=season, episode=episode)
        self.open_dialog(dialog, prev_window)

    def open_actor_info(self, prev_window=None, actor_id=None, name=None):
        """
       open actor info, deal with window stack
        """
        import DialogActorInfo
        dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, name=name)
        self.open_dialog(dialog, prev_window)

    def open_video_list(self, prev_window=None, listitems=None, filters=[], mode="filter", list_id=False, filter_label="", force=False, media_type="movie"):
        """
       open video list, deal with window stack and color
        """
        import DialogVideoList
        if prev_window:
            try:  # TODO rework
                color = prev_window.data["general"]['ImageColor']
            except:
                color = "FFFFFFFF"
        else:
            color = "FFFFFFFF"
        dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % ADDON_NAME, ADDON_PATH, listitems=listitems, color=color, filters=filters, mode=mode, list_id=list_id, force=force, filter_label=filter_label, type=media_type)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
        dialog.doModal()

    def open_youtube_list(self, prev_window=None, search_string="", filters=[], sort="relevance", filter_label="", force=False, media_type="videos"):
        """
       open video list, deal with window stack and color
        """
        import DialogYoutubeList
        if prev_window:
            try:  # TODO rework
                color = prev_window.data["general"]['ImageColor']
            except:
                color = "FFFFFFFF"
        else:
            color = "FFFFFFFF"
        dialog = DialogYoutubeList.DialogYoutubeList(u'script-%s-YoutubeList.xml' % ADDON_NAME, ADDON_PATH, search_string=search_string, color=color, filters=filters, force=force, filter_label=filter_label, type=media_type)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
        dialog.doModal()

    def open_dialog(self, dialog, prev_window):
        if dialog.data:
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()

wm = WindowManager()
