# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui

from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB as tmdb
from resources.lib.WindowManager import wm

from kodi65 import addon
from DialogBaseInfo import DialogBaseInfo
from ActionHandler import ActionHandler

ID_LIST_SIMILAR = 150
ID_LIST_SEASONS = 250
ID_LIST_NETWORKS = 1450
ID_LIST_STUDIOS = 550
ID_LIST_CERTS = 650
ID_LIST_CREW = 750
ID_LIST_GENRES = 850
ID_LIST_KEYWORDS = 950
ID_LIST_ACTORS = 1000
ID_LIST_VIDEOS = 1150
ID_LIST_IMAGES = 1250
ID_LIST_BACKDROPS = 1350

ID_BUTTON_BROWSE = 120
ID_BUTTON_PLOT = 132
ID_BUTTON_MANAGE = 445
ID_BUTTON_SETRATING = 6001
ID_BUTTON_OPENLIST = 6002
ID_BUTTON_FAV = 6003
ID_BUTTON_RATED = 6006

ch = ActionHandler()


def get_window(window_type):

    class DialogTVShowInfo(DialogBaseInfo, window_type):
        TYPE = "TVShow"
        LISTS = [(ID_LIST_SIMILAR, "similar"),
                 (ID_LIST_SEASONS, "seasons"),
                 (ID_LIST_NETWORKS, "networks"),
                 (ID_LIST_STUDIOS, "studios"),
                 (ID_LIST_CERTS, "certifications"),
                 (ID_LIST_CREW, "crew"),
                 (ID_LIST_GENRES, "genres"),
                 (ID_LIST_KEYWORDS, "keywords"),
                 (ID_LIST_ACTORS, "actors"),
                 (ID_LIST_VIDEOS, "videos"),
                 (ID_LIST_IMAGES, "images"),
                 (ID_LIST_BACKDROPS, "backdrops")]

        def __init__(self, *args, **kwargs):
            super(DialogTVShowInfo, self).__init__(*args, **kwargs)
            data = tmdb.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False),
                                             dbid=self.dbid)
            if not data:
                return None
            self.info, self.data, self.states = data
            if not self.info.get_property("dbid"):
                self.info.set_art("poster", Utils.get_file(self.info.get_art("poster")))
            self.info.update_properties(ImageTools.blur(self.info.get_art("poster")))

        def onInit(self):
            self.get_youtube_vids("%s tv" % (self.info.get_info("title")))
            super(DialogTVShowInfo, self).onInit()
            super(DialogTVShowInfo, self).update_states()

        def onClick(self, control_id):
            super(DialogTVShowInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(ID_BUTTON_BROWSE)
        def browse_tvshow(self, control_id):
            self.close()
            xbmc.executebuiltin("Dialog.Close(all)")
            xbmc.executebuiltin("ActivateWindow(videos,videodb://tvshows/titles/%s/)" % self.dbid)

        @ch.click(ID_LIST_SEASONS)
        def open_season_dialog(self, control_id):
            info = self.FocusedItem(control_id).getVideoInfoTag()
            wm.open_season_info(prev_window=self,
                                tvshow_id=self.info.get_property("id"),
                                season=info.getSeason(),
                                tvshow=self.info.get_info("title"))

        @ch.click(ID_LIST_STUDIOS)
        def open_company_info(self, control_id):
            filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                        "type": "with_companies",
                        "typelabel": addon.LANG(20388),
                        "label": self.FocusedItem(control_id).getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)

        @ch.click(ID_LIST_KEYWORDS)
        def open_keyword_info(self, control_id):
            filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                        "type": "with_keywords",
                        "typelabel": addon.LANG(32114),
                        "label": self.FocusedItem(control_id).getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)

        @ch.click(ID_LIST_GENRES)
        def open_genre_info(self, control_id):
            filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                        "type": "with_genres",
                        "typelabel": addon.LANG(135),
                        "label": self.FocusedItem(control_id).getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")

        @ch.click(ID_LIST_NETWORKS)
        def open_network_info(self, control_id):
            filters = [{"id": self.FocusedItem(control_id).getProperty("id"),
                        "type": "with_networks",
                        "typelabel": addon.LANG(32152),
                        "label": self.FocusedItem(control_id).getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")

        @ch.click(ID_BUTTON_MANAGE)
        def show_manage_dialog(self, control_id):
            options = []
            title = self.info.get_info("tvshowtitle")
            if self.dbid:
                call = "RunScript(script.artwork.downloader,mediatype=tv,%s)"
                options += [[addon.LANG(413), call % ("mode=gui,dbid=" + self.dbid)],
                            [addon.LANG(14061), call % ("dbid=" + self.dbid)],
                            [addon.LANG(32101), call % ("mode=custom,dbid=" + self.dbid + ",extrathumbs")],
                            [addon.LANG(32100), call % ("mode=custom,dbid=" + self.dbid)]]
            else:
                options += [[addon.LANG(32166), "RunPlugin(plugin://plugin.video.sickrage?action=addshow&show_name=%s)" % title]]
            if xbmc.getCondVisibility("system.hasaddon(script.libraryeditor)") and self.dbid:
                options.append([addon.LANG(32103), "RunScript(script.libraryeditor,DBID=" + self.dbid + ")"])
            options.append([addon.LANG(1049), "Addon.OpenSettings(script.extendedinfo)"])
            selection = xbmcgui.Dialog().select(heading=addon.LANG(32133),
                                                list=[item[0] for item in options])
            if selection == -1:
                return None
            for item in options[selection][1].split("||"):
                xbmc.executebuiltin(item)

        @ch.click(ID_BUTTON_SETRATING)
        def set_rating(self, control_id):
            rating = Utils.get_rating_from_selectdialog()
            if tmdb.set_rating(media_type="tv",
                               media_id=self.info.get_property("id"),
                               rating=rating,
                               dbid=self.info.get_property("dbid")):
                self.update_states()

        @ch.click(ID_BUTTON_OPENLIST)
        def open_list(self, control_id):
            index = xbmcgui.Dialog().select(heading=addon.LANG(32136),
                                            list=[addon.LANG(32144), addon.LANG(32145)])
            if index == 0:
                wm.open_video_list(prev_window=self,
                                   media_type="tv",
                                   mode="favorites")
            elif index == 1:
                wm.open_video_list(prev_window=self,
                                   mode="rating",
                                   media_type="tv")

        @ch.click(ID_BUTTON_FAV)
        def toggle_fav_status(self, control_id):
            tmdb.change_fav_status(media_id=self.info.get_property("id"),
                                   media_type="tv",
                                   status=str(not bool(self.states["favorite"])).lower())
            self.update_states()

        @ch.click(ID_BUTTON_RATED)
        def open_rated_items(self, control_id):
            wm.open_video_list(prev_window=self,
                               mode="rating",
                               media_type="tv")

        @ch.click(ID_BUTTON_PLOT)
        def open_text(self, control_id):
            xbmcgui.Dialog().textviewer(heading=addon.LANG(32037),
                                        text=self.info.get_info("plot"))

        def update_states(self):
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, self.states = tmdb.extended_tvshow_info(tvshow_id=self.info.get_property("id"),
                                                           cache_time=0,
                                                           dbid=self.dbid)
            super(DialogTVShowInfo, self).update_states()

    return DialogTVShowInfo
