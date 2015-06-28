# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcgui
from ..Utils import *
from ..ImageTools import *
from ..TheMovieDB import *
from ..YouTube import *
from DialogBaseInfo import DialogBaseInfo
from ..WindowManager import wm
from .. import VideoPlayer
from ..OnClickHandler import OnClickHandler

PLAYER = VideoPlayer.VideoPlayer()
ch = OnClickHandler()


class DialogActorInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogActorInfo, self).__init__(*args, **kwargs)
        self.id = kwargs.get('id', False)
        self.type = "Actor"
        if not self.id:
            notify(LANG(32143))
            return None
        data = extended_actor_info(actor_id=self.id)
        if data:
            self.info, self.data = data
        else:
            notify(LANG(32143))
            return None
        youtube_thread = GetYoutubeVidsThread(search_str=self.info["name"])
        youtube_thread.start()
        filter_thread = FilterImageThread(image=self.info["thumb"])
        filter_thread.start()
        db_movies = len([item for item in self.data["movie_roles"] if "dbid" in item])
        self.info["DBMovies"] = str(db_movies)
        movie_crew_roles = merge_dict_lists(self.data["movie_crew_roles"])
        tvshow_crew_roles = merge_dict_lists(self.data["tvshow_crew_roles"])
        filter_thread.join()
        self.info['ImageFilter'] = filter_thread.image
        self.info['ImageColor'] = filter_thread.imagecolor
        youtube_thread.join()
        self.listitems = [(150, create_listitems(self.data["movie_roles"], 0)),
                          (250, create_listitems(self.data["tvshow_roles"], 0)),
                          (450, create_listitems(self.data["images"], 0)),
                          (550, create_listitems(movie_crew_roles, 0)),
                          (650, create_listitems(tvshow_crew_roles, 0)),
                          (750, create_listitems(self.data["tagged_images"], 0)),
                          (350, create_listitems(youtube_thread.listitems, 0))]

    def onInit(self):
        super(DialogActorInfo, self).onInit()
        pass_dict_to_skin(data=self.info,
                          prefix="actor.",
                          window_id=self.window_id)
        self.fill_lists()

    @ch.click(150)
    @ch.click(550)
    def open_movie_info(self):
        wm.open_movie_info(prev_window=self,
                           movie_id=self.control.getSelectedItem().getProperty("id"),
                           dbid=self.control.getSelectedItem().getProperty("dbid"))

    @ch.click(250)
    @ch.click(650)
    def open_tvshow_dialog(self):
        selection = xbmcgui.Dialog().select(heading=LANG(32151),
                                            list=[LANG(32147), LANG(32148)])
        if selection == 0:
            self.open_credit_dialog(credit_id=self.control.getSelectedItem().getProperty("credit_id"))
        if selection == 1:
            wm.open_tvshow_info(prev_window=self,
                                tvshow_id=self.control.getSelectedItem().getProperty("id"),
                                dbid=self.control.getSelectedItem().getProperty("dbid"))

    @ch.click(450)
    @ch.click(750)
    def open_image(self):
        wm.open_slideshow(image=self.control.getSelectedItem().getProperty("original"))

    @ch.click(350)
    def play_youtube_video(self):
        PLAYER.play_youtube_video(youtube_id=self.control.getSelectedItem().getProperty("youtube_id"),
                                  listitem=self.control.getSelectedItem(),
                                  window=self)

    @ch.click(132)
    def show_plot(self):
        wm.open_textviewer(header=LANG(32037),
                           text=self.info["biography"],
                           color=self.info['ImageColor'])

    def onClick(self, control_id):
        ch.serve(control_id, self)

