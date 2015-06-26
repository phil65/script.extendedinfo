# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from Utils import *
from TheMovieDB import *
from YouTube import *
from ImageTools import *
from BaseClasses import DialogBaseInfo
from WindowManager import wm
from OnClickHandler import OnClickHandler
import VideoPlayer

ch = OnClickHandler()
PLAYER = VideoPlayer.VideoPlayer()


class DialogSeasonInfo(DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogSeasonInfo, self).__init__(*args, **kwargs)
        self.tmdb_id = kwargs.get('id')
        self.season = kwargs.get('season')
        self.tvshow = kwargs.get('tvshow')
        if self.season and (self.tmdb_id or self.tvshow):
            data = extended_season_info(tmdb_tvshow_id=self.tmdb_id,
                                        tvshow_name=self.tvshow,
                                        season_number=self.season)
            if data:
                self.info, self.data = data
            else:
                notify(LANG(32143))
                return None
            search_str = "%s %s tv" % (self.info["TVShowTitle"], self.info['title'])
            youtube_thread = GetYoutubeVidsThread(search_str, "", "relevance", 15)
            youtube_thread.start()
            if "dbid" not in self.info:  # need to add comparing for seasons
                self.info['Poster'] = get_file(url=self.info["Poster"])
            filter_thread = FilterImageThread(self.info["Poster"], 25)
            filter_thread.start()
            youtube_thread.join()
            filter_thread.join()
            self.info['ImageFilter'], self.info['ImageColor'] = filter_thread.image, filter_thread.imagecolor
            self.listitems = [(1000, create_listitems(self.data["actors"], 0)),
                              (750, create_listitems(self.data["crew"], 0)),
                              (2000, create_listitems(self.data["episodes"], 0)),
                              (1150, create_listitems(self.data["videos"], 0)),
                              (1250, create_listitems(self.data["images"], 0)),
                              (1350, create_listitems(self.data["backdrops"], 0)),
                              (350, create_listitems(youtube_thread.listitems, 0))]
        else:
            notify(LANG(32143))

    def onInit(self):
        super(DialogSeasonInfo, self).onInit()
        self.window.setProperty("type", "season")
        pass_dict_to_skin(data=self.info,
                          prefix="movie.",
                          window_id=self.window_id)
        self.fill_lists()

    @ch.click(750)
    @ch.click(1000)
    def open_actor_info(self):
        wm.open_actor_info(prev_window=self,
                           actor_id=self.control.getSelectedItem().getProperty("id"))

    @ch.click(2000)
    def open_episode_info(self):
        if not self.tmdb_id:
            response = get_tmdb_data("search/tv?query=%s&language=%s&" % (urllib.quote_plus(self.tvshow), ADDON.getSetting("LanguageID")), 30)
            self.tmdb_id = str(response['results'][0]['id'])
        wm.open_episode_info(prev_window=self,
                             tvshow_id=self.tmdb_id,
                             season=self.control.getSelectedItem().getProperty("season"),
                             episode=self.control.getSelectedItem().getProperty("episode"))

    @ch.click(350)
    @ch.click(1150)
    def play_youtube_video(self):
        PLAYER.play_youtube_video(youtube_id=self.control.getSelectedItem().getProperty("youtube_id"),
                                  listitem=self.control.getSelectedItem(),
                                  window=self)

    @ch.click(1250)
    @ch.click(1350)
    def open_image(self):
        wm.open_slideshow(image=self.control.getSelectedItem().getProperty("original"))

    @ch.click(132)
    def open_text(self):
        wm.open_textviewer(header=LANG(32037),
                           text=self.info["Plot"],
                           color=self.info['ImageColor'])

    def onClick(self, control_id):
        ch.serve(control_id, self)
