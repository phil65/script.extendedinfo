# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from Utils import *
from TheMovieDB import *
import xbmcaddon
from local_db import get_imdb_id_from_db
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")


class WindowManager(object):
    window_stack = []

    def __init__(self):
        self.reopen_window = False

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
        elif self.reopen_window:
            xbmc.sleep(500)
            xbmc.executebuiltin("Action(Info)")

    def open_movie_info(self, prev_window=None, movie_id=None, dbid=None, name=None, imdb_id=None):
        """
        open movie info, deal with window stack
        """
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        from dialogs import DialogVideoInfo
        if not movie_id:
            movie_id = get_movie_tmdb_id(imdb_id=imdb_id,
                                         dbid=dbid,
                                         name=name)
        dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH,
                                                 id=movie_id)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_tvshow_info(self, prev_window=None, tvshow_id=None, dbid=None, tvdb_id=None, imdb_id=None, name=None):
        """
        open tvshow info, deal with window stack
        """
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        from dialogs import DialogTVShowInfo
        tmdb_id = None
        if tvshow_id:
            tmdb_id = tvshow_id
        elif dbid and (int(dbid) > 0):
            tvdb_id = get_imdb_id_from_db(media_type="tvshow",
                                          dbid=dbid)
            if tvdb_id:
                tmdb_id = get_show_tmdb_id(tvdb_id)
        elif tvdb_id:
            tmdb_id = get_show_tmdb_id(tvdb_id)
        elif imdb_id:
            tmdb_id = get_show_tmdb_id(tvdb_id=imdb_id,
                                       source="imdb_id")
        elif name:
            tmdb_id = search_media(media_name=name,
                                   year="",
                                   media_type="tv")
        dialog = DialogTVShowInfo.DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH,
                                                   tmdb_id=tmdb_id,
                                                   dbid=dbid)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_season_info(self, prev_window=None, tvshow_id=None, season=None, tvshow=None):
        """
        open season info, deal with window stack
        needs *season AND (*tvshow_id OR *tvshow)
        """
        from dialogs import DialogSeasonInfo
        dialog = DialogSeasonInfo.DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH,
                                                   id=tvshow_id,
                                                   season=season,
                                                   tvshow=tvshow)
        self.open_dialog(dialog, prev_window)

    def open_episode_info(self, prev_window=None, tvshow_id=None, season=None, episode=None, tvshow=None):
        """
        open season info, deal with window stack
        needs *tvshow_id AND *season AND *episode
        """
        from dialogs import DialogEpisodeInfo
        dialog = DialogEpisodeInfo.DialogEpisodeInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH,
                                                     show_id=tvshow_id,
                                                     tvshow=tvshow,
                                                     season=season,
                                                     episode=episode)
        self.open_dialog(dialog, prev_window)

    def open_actor_info(self, prev_window=None, actor_id=None, name=None):
        """
        open actor info, deal with window stack
        """
        from dialogs import DialogActorInfo
        if not actor_id:
            name = name.decode("utf-8").split(" " + LANG(20347) + " ")
            names = name[0].strip().split(" / ")
            if len(names) > 1:
                ret = xbmcgui.Dialog().select(heading=LANG(32027),
                                              list=names)
                if ret == -1:
                    return None
                name = names[ret]
            else:
                name = names[0]
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            actor_info = get_person_info(name)
            if actor_info:
                actor_id = actor_info["id"]
        else:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
        dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH,
                                                 id=actor_id)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_video_list(self, prev_window=None, listitems=None, filters=[], mode="filter", list_id=False, filter_label="", force=False, media_type="movie"):
        """
        open video list, deal with window stack and color
        """
        from dialogs import DialogVideoList
        if prev_window:
            try:  # TODO rework
                color = prev_window.data["general"]['ImageColor']
            except:
                color = "FFFFFFFF"
        else:
            color = "FFFFFFFF"
        dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % ADDON_NAME, ADDON_PATH,
                                                 listitems=listitems,
                                                 color=color,
                                                 filters=filters,
                                                 mode=mode,
                                                 list_id=list_id,
                                                 force=force,
                                                 filter_label=filter_label,
                                                 type=media_type)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
        dialog.doModal()

    def open_youtube_list(self, prev_window=None, search_str="", filters=[], sort="relevance", filter_label="", force=False, media_type="video"):
        """
        open video list, deal with window stack and color
        """
        from dialogs import DialogYoutubeList
        if prev_window:
            try:  # TODO rework
                color = prev_window.data["general"]['ImageColor']
            except:
                color = "FFFFFFFF"
        else:
            color = "FFFFFFFF"
        dialog = DialogYoutubeList.DialogYoutubeList(u'script-%s-YoutubeList.xml' % ADDON_NAME, ADDON_PATH,
                                                     search_str=search_str,
                                                     color=color,
                                                     filters=filters,
                                                     force=force,
                                                     filter_label=filter_label,
                                                     type=media_type)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
        dialog.doModal()

    def open_slideshow(self, image):
        """
        open slideshow dialog for single image
        """
        from dialogs import SlideShow
        dialog = SlideShow.SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH,
                                     image=image)
        dialog.doModal()

    def open_textviewer(self, header="", text="", color="FFFFFFFF"):
        """
        open textviewer dialog
        """
        from dialogs.TextViewerDialog import TextViewerDialog
        w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH,
                             header=header,
                             text=text,
                             color=color)
        w.doModal()

    def open_selectdialog(self, listitems):
        """
        open selectdialog, return listitem dict and index
        """
        from dialogs.SelectDialog import SelectDialog
        w = SelectDialog('DialogSelect.xml', ADDON_PATH,
                         listing=listitems)
        w.doModal()
        return w.listitem, w.index

    def open_dialog(self, dialog, prev_window):
        if dialog.data:
            if xbmc.getCondVisibility("Window.IsVisible(movieinformation)"):
                xbmc.executebuiltin("Dialog.Close(movieinformation)")
                self.reopen_window = True
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()

wm = WindowManager()
