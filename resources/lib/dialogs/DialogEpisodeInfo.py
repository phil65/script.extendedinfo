# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc

from resources.lib import TheMovieDB as tmdb
from resources.lib.WindowManager import wm
from DialogVideoInfo import DialogVideoInfo

from kodi65 import imagetools
from kodi65 import utils
from ActionHandler import ActionHandler

ID_LIST_YOUTUBE = 350
ID_LIST_CREW = 750
ID_LIST_ACTORS = 1000
ID_LIST_VIDEOS = 1150
ID_LIST_BACKDROPS = 1350
ID_BUTTON_RATED = 6006

ch = ActionHandler()


def get_window(window_type):

    class DialogEpisodeInfo(DialogVideoInfo, window_type):
        TYPE = "Episode"
        TYPE_ALT = "episode"
        LISTS = [(ID_LIST_ACTORS, "actors"),
                 (ID_LIST_CREW, "crew"),
                 (ID_LIST_VIDEOS, "videos"),
                 (ID_LIST_BACKDROPS, "images")]

        @utils.busy_dialog
        def __init__(self, *args, **kwargs):
            super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
            self.tvshow_id = kwargs.get('tvshow_id')
            data = tmdb.extended_episode_info(tvshow_id=self.tvshow_id,
                                              season=kwargs.get('season'),
                                              episode=kwargs.get('episode'))
            if not data:
                return None
            self.info, self.lists, self.states = data
            self.info.update_properties(imagetools.blur(self.info.get_art("thumb")))

        def onInit(self):
            super(DialogEpisodeInfo, self).onInit()
            self.get_youtube_vids("{} {}x{}".format(self.info.get_info("tvshowtitle"),
                                                    self.info.get_info('season'),
                                                    self.info.get_info('episode')))
            super(DialogEpisodeInfo, self).update_states()

        def onClick(self, control_id):
            super(DialogEpisodeInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(ID_BUTTON_RATED)
        def open_rating_list(self, control_id):
            wm.show_busy()
            listitems = tmdb.get_rated_media_items("tv/episodes")
            wm.hide_busy()
            wm.open_video_list(listitems=listitems)

        def get_identifier(self):
            return [self.tvshow_id, self.info.get_info("season"), self.info.get_info("episode")]

        def update_states(self):
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, self.states = tmdb.extended_episode_info(tvshow_id=self.tvshow_id,
                                                            season=self.info.get_info("season"),
                                                            episode=self.info.get_info("episode"),
                                                            cache_time=0)
            super(DialogEpisodeInfo, self).update_states()

    return DialogEpisodeInfo
