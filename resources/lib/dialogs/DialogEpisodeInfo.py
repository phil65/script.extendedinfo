# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui

from resources.lib import Utils
from resources.lib import TheMovieDB as tmdb
from resources.lib import ImageTools
from resources.lib.WindowManager import wm
from DialogBaseInfo import DialogBaseInfo

from kodi65 import addon
from kodi65 import utils
from ActionHandler import ActionHandler

ID_CONTROL_PLOT = 132
ID_LIST_YOUTUBE = 350
ID_LIST_CREW = 750
ID_LIST_ACTORS = 1000
ID_LIST_VIDEOS = 1150
ID_LIST_BACKDROPS = 1350
ID_CONTROL_SETRATING = 6001
ID_CONTROL_RATINGLISTS = 6006

ch = ActionHandler()


def get_window(window_type):

    class DialogEpisodeInfo(DialogBaseInfo, window_type):
        TYPE = "Episode"
        LISTS = [(ID_LIST_ACTORS, "actors"),
                 (ID_LIST_CREW, "crew"),
                 (ID_LIST_VIDEOS, "videos"),
                 (ID_LIST_BACKDROPS, "images")]

        @utils.busy_dialog
        def __init__(self, *args, **kwargs):
            super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
            self.tvshow_id = kwargs.get('show_id')
            data = tmdb.extended_episode_info(tvshow_id=self.tvshow_id,
                                              season=kwargs.get('season'),
                                              episode=kwargs.get('episode'))
            if not data:
                return None
            self.info, self.data, self.states = data
            self.info.update_properties(ImageTools.blur(self.info.get("thumb")))

        def onInit(self):
            super(DialogEpisodeInfo, self).onInit()
            self.get_youtube_vids("%s tv" % (self.info.get_info('title')))
            super(DialogEpisodeInfo, self).update_states()

        def onClick(self, control_id):
            super(DialogEpisodeInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(ID_CONTROL_PLOT)
        def open_text(self, control_id):
            xbmcgui.Dialog().textviewer(heading=addon.LANG(32037),
                                        text=self.info.get_info("plot"))

        @ch.click(ID_CONTROL_SETRATING)
        def set_rating_dialog(self, control_id):
            rating = Utils.get_rating_from_selectdialog()
            if tmdb.set_rating(media_type="episode",
                               media_id=[self.tvshow_id,
                                         self.info.get_info("season"),
                                         self.info.get_info("episode")],
                               rating=rating):
                self.update_states()

        @ch.click(ID_CONTROL_RATINGLISTS)
        def open_rating_list(self, control_id):
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = tmdb.get_rated_media_items("tv/episodes")
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            wm.open_video_list(prev_window=self,
                               listitems=listitems)

        def update_states(self):
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, self.states = tmdb.extended_episode_info(tvshow_id=self.tvshow_id,
                                                            season=self.info.get_info("season"),
                                                            episode=self.info.get_info("episode"),
                                                            cache_time=0)
            super(DialogEpisodeInfo, self).update_states()

    return DialogEpisodeInfo
