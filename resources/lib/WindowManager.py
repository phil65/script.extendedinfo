# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import os
import re

import xbmc
import xbmcgui
import xbmcvfs

import TheMovieDB

import windows
from kodi65 import addon
from kodi65 import utils
from kodi65.player import player
from kodi65.localdb import local_db

INFO_XML_CLASSIC = u'script-%s-DialogVideoInfo.xml' % (addon.NAME)
LIST_XML_CLASSIC = u'script-%s-VideoList.xml' % (addon.NAME)
ACTOR_XML_CLASSIC = u'script-%s-DialogInfo.xml' % (addon.NAME)
if addon.bool_setting("force_native_layout") and addon.setting("xml_version") != addon.VERSION:
    addon.set_setting("xml_version", addon.VERSION)
    INFO_XML = u'script-%s-DialogVideoInfo-classic.xml' % (addon.NAME)
    LIST_XML = u'script-%s-VideoList-classic.xml' % (addon.NAME)
    ACTOR_XML = u'script-%s-DialogInfo-classic.xml' % (addon.NAME)
    path = os.path.join(addon.PATH, "resources", "skins", "Default", "1080i")
    xbmcvfs.copy(strSource=os.path.join(path, INFO_XML_CLASSIC),
                 strDestnation=os.path.join(path, INFO_XML))
    xbmcvfs.copy(strSource=os.path.join(path, LIST_XML_CLASSIC),
                 strDestnation=os.path.join(path, LIST_XML))
    xbmcvfs.copy(strSource=os.path.join(path, ACTOR_XML_CLASSIC),
                 strDestnation=os.path.join(path, ACTOR_XML))
else:
    INFO_XML = INFO_XML_CLASSIC
    LIST_XML = LIST_XML_CLASSIC
    ACTOR_XML = ACTOR_XML_CLASSIC


class WindowManager(object):
    window_stack = []

    def __init__(self):
        self.active_dialog = None
        self.saved_background = addon.get_global("infobackground")
        self.monitor = SettingsMonitor()

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
            self.active_dialog = self.window_stack.pop()
            xbmc.sleep(300)
            self.active_dialog.doModal()
        else:
            addon.set_global("infobackground", self.saved_background)

    def cancel(self, window):
        addon.set_global("infobackground", self.saved_background)
        self.window_stack = []
        window.close()

    def open_movie_info(self, prev_window=None, movie_id=None, dbid=None,
                        name=None, imdb_id=None):
        """
        open movie info, deal with window stack
        """
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        from dialogs import DialogMovieInfo
        dbid = int(dbid) if dbid and int(dbid) > 0 else None
        if not movie_id:
            movie_id = TheMovieDB.get_movie_tmdb_id(imdb_id=imdb_id,
                                                    dbid=dbid,
                                                    name=name)
        movie_class = DialogMovieInfo.get_window(windows.DialogXML)
        dialog = movie_class(INFO_XML,
                             addon.PATH,
                             id=movie_id,
                             dbid=dbid)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_tvshow_info(self, prev_window=None, tmdb_id=None, dbid=None,
                         tvdb_id=None, imdb_id=None, name=None):
        """
        open tvshow info, deal with window stack
        """
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        dbid = int(dbid) if dbid and int(dbid) > 0 else None
        from dialogs import DialogTVShowInfo
        if tmdb_id:
            pass
        elif tvdb_id:
            tmdb_id = TheMovieDB.get_show_tmdb_id(tvdb_id)
        elif imdb_id:
            tmdb_id = TheMovieDB.get_show_tmdb_id(tvdb_id=imdb_id,
                                                  source="imdb_id")
        elif dbid:
            tvdb_id = local_db.get_imdb_id(media_type="tvshow",
                                           dbid=dbid)
            if tvdb_id:
                tmdb_id = TheMovieDB.get_show_tmdb_id(tvdb_id)
        elif name:
            tmdb_id = TheMovieDB.search_media(media_name=name,
                                              year="",
                                              media_type="tv")
        tvshow_class = DialogTVShowInfo.get_window(windows.DialogXML)
        dialog = tvshow_class(INFO_XML,
                              addon.PATH,
                              tmdb_id=tmdb_id,
                              dbid=dbid)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_season_info(self, prev_window=None, tvshow_id=None,
                         season=None, tvshow=None, dbid=None):
        """
        open season info, deal with window stack
        needs *season AND (*tvshow_id OR *tvshow)
        """
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        from dialogs import DialogSeasonInfo
        dbid = int(dbid) if dbid and int(dbid) > 0 else None
        if not tvshow_id:
            params = {"query": tvshow,
                      "language": addon.setting("language")}
            response = TheMovieDB.get_data(url="search/tv",
                                           params=params,
                                           cache_days=30)
            if response["results"]:
                tvshow_id = str(response['results'][0]['id'])
            else:
                params = {"query": re.sub('\(.*?\)', '', tvshow),
                          "language": addon.setting("language")}
                response = TheMovieDB.get_data(url="search/tv",
                                               params=params,
                                               cache_days=30)
                if response["results"]:
                    tvshow_id = str(response['results'][0]['id'])

        season_class = DialogSeasonInfo.get_window(windows.DialogXML)
        dialog = season_class(INFO_XML,
                              addon.PATH,
                              id=tvshow_id,
                              season=season,
                              dbid=dbid)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_episode_info(self, prev_window=None, tvshow_id=None, season=None,
                          episode=None, tvshow=None, dbid=None):
        """
        open season info, deal with window stack
        needs (*tvshow_id OR *tvshow) AND *season AND *episode
        """
        from dialogs import DialogEpisodeInfo
        dbid = int(dbid) if dbid and int(dbid) > 0 else None
        ep_class = DialogEpisodeInfo.get_window(windows.DialogXML)
        if not tvshow_id and tvshow:
            tvshow_id = TheMovieDB.search_media(media_name=tvshow,
                                                media_type="tv",
                                                cache_days=7)
        dialog = ep_class(INFO_XML,
                          addon.PATH,
                          tvshow_id=tvshow_id,
                          season=season,
                          episode=episode,
                          dbid=dbid)
        self.open_dialog(dialog, prev_window)

    def open_actor_info(self, prev_window=None, actor_id=None, name=None):
        """
        open actor info, deal with window stack
        """
        from dialogs import DialogActorInfo
        if not actor_id:
            name = name.split(" " + addon.LANG(20347) + " ")
            names = name[0].strip().split(" / ")
            if len(names) > 1:
                ret = xbmcgui.Dialog().select(heading=addon.LANG(32027),
                                              list=names)
                if ret == -1:
                    return None
                name = names[ret]
            else:
                name = names[0]
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            actor_info = TheMovieDB.get_person_info(name)
            if actor_info:
                actor_id = actor_info["id"]
            else:
                return None
        else:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
        actor_class = DialogActorInfo.get_window(windows.DialogXML)
        dialog = actor_class(ACTOR_XML,
                             addon.PATH,
                             id=actor_id)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.open_dialog(dialog, prev_window)

    def open_video_list(self, prev_window=None, listitems=None, filters=None, mode="filter", list_id=False,
                        filter_label="", force=False, media_type="movie", search_str=""):
        """
        open video list, deal with window stack and color
        """
        filters = [] if not filters else filters
        from dialogs import DialogVideoList
        if prev_window:
            try:  # TODO rework
                color = prev_window.data["general"]['ImageColor']
            except Exception:
                color = "FFFFFFFF"
        else:
            color = "FFFFFFFF"
        check_version()
        browser_class = DialogVideoList.get_window(windows.DialogXML)
        dialog = browser_class(LIST_XML,
                               addon.PATH,
                               listitems=listitems,
                               color=color,
                               filters=filters,
                               mode=mode,
                               list_id=list_id,
                               force=force,
                               filter_label=filter_label,
                               search_str=search_str,
                               type=media_type)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
        dialog.doModal()

    def open_youtube_list(self, prev_window=None, search_str="", filters=None, sort="relevance",
                          filter_label="", media_type="video"):
        """
        open video list, deal with window stack and color
        """
        filters = [] if not filters else filters
        from dialogs import DialogYoutubeList
        if prev_window:
            try:  # TODO rework
                color = prev_window.data["general"]['ImageColor']
            except Exception:
                color = "FFFFFFFF"
        else:
            color = "FFFFFFFF"
        youtube_class = DialogYoutubeList.get_window(windows.WindowXML)
        dialog = youtube_class(u'script-%s-YoutubeList.xml' % addon.NAME, addon.PATH,
                               search_str=search_str,
                               color=color,
                               filters=filters,
                               filter_label=filter_label,
                               type=media_type)
        if prev_window:
            self.add_to_stack(prev_window)
            prev_window.close()
        dialog.doModal()

    def open_dialog(self, dialog, prev_window):
        if dialog.data:
            self.active_dialog = dialog
            check_version()
            if prev_window:
                self.add_to_stack(prev_window)
                prev_window.close()
            dialog.doModal()
        else:
            self.active_dialog = None
            utils.notify(addon.LANG(32143))

    def play_youtube_video(self, youtube_id="", listitem=None, window=False):
        """
        play youtube vid with info from *listitem
        """
        url, yt_listitem = player.youtube_info_by_id(youtube_id)
        if not listitem:
            listitem = yt_listitem
        if url:
            if window and window.window_type == "dialog":
                self.add_to_stack(window)
                window.close()
            xbmc.executebuiltin("Dialog.Close(movieinformation)")
            xbmc.Player().play(item=url,
                               listitem=listitem,
                               windowed=False,
                               startpos=-1)
            if window and window.window_type == "dialog":
                player.wait_for_video_end()
                self.pop_stack()
        else:
            utils.notify(header=addon.LANG(257),
                         message="no youtube id found")


def check_version():
    """
    check version, open TextViewer if update detected
    """
    if not addon.setting("changelog_version") == addon.VERSION:
        text = utils.read_from_file(os.path.join(addon.PATH, "changelog.txt"), True)
        xbmcgui.Dialog().textviewer(heading=addon.LANG(24036),
                                    text=text)
        addon.set_setting("changelog_version", addon.VERSION)
    if not addon.setting("first_start_infodialog"):
        addon.set_setting("first_start_infodialog", "True")
        xbmcgui.Dialog().ok(heading=addon.NAME,
                            line1=addon.LANG(32140),
                            line2=addon.LANG(32141))


class SettingsMonitor(xbmc.Monitor):

    def __init__(self):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        addon.reload_addon()
        username = addon.setting("tmdb_username")
        password = addon.setting("tmdb_password")
        if username and password:
            TheMovieDB.Login = TheMovieDB.LoginProvider(username=username,
                                                        password=password)
        if wm.active_dialog:
            wm.active_dialog.close()
            wm.active_dialog.logged_in = TheMovieDB.Login.check_login(cache_days=0)
            wm.active_dialog.doModal()


wm = WindowManager()
