# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
from ..Utils import *
from ..TheMovieDB import *
from ..YouTube import *
from ..ImageTools import *
from BaseClasses import DialogBaseInfo
from ..WindowManager import wm
from ..OnClickHandler import OnClickHandler
import VideoPlayer

PLAYER = VideoPlayer.VideoPlayer()
ch = OnClickHandler()


class DialogEpisodeInfo(DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
        self.tmdb_id = kwargs.get('show_id')
        self.season = kwargs.get('season')
        self.show_name = kwargs.get('tvshow')
        self.episode_number = kwargs.get('episode')
        data = extended_episode_info(tvshow_id=self.tmdb_id,
                                     season=self.season,
                                     episode=self.episode_number)
        if data:
            self.info, self.data, self.account_states = data
        else:
            notify(LANG(32143))
            return None
        search_str = "%s tv" % (self.info['title'])
        youtube_thread = GetYoutubeVidsThread(search_str=search_str)
        youtube_thread.start()  # TODO: rem threading here
        filter_thread = FilterImageThread(self.info["thumb"], 25)
        filter_thread.start()
        youtube_thread.join()
        filter_thread.join()
        self.info['ImageFilter'] = filter_thread.image
        self.info['ImageColor'] = filter_thread.imagecolor
        self.listitems = [(1000, create_listitems(self.data["actors"] + self.data["guest_stars"], 0)),
                          (750, create_listitems(self.data["crew"], 0)),
                          (1150, create_listitems(self.data["videos"], 0)),
                          (1350, create_listitems(self.data["images"], 0)),
                          (350, create_listitems(youtube_thread.listitems, 0))]

    def onInit(self):
        super(DialogEpisodeInfo, self).onInit()
        self.window.setProperty("type", "Episode")
        pass_dict_to_skin(self.info, "movie.", False, False, self.window_id)
        self.fill_lists()

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

    @ch.click(750)
    @ch.click(1000)
    def open_actor_info(self):
        wm.open_actor_info(prev_window=self,
                           actor_id=self.control.getSelectedItem().getProperty("id"))

    @ch.click(132)
    def open_text(self):
        wm.open_textviewer(header=LANG(32037),
                           text=self.info["Plot"],
                           color=self.info['ImageColor'])

    @ch.click(6001)
    def set_rating_dialog(self):
        rating = get_rating_from_user()
        if not rating:
            return None
        identifier = [self.tmdb_id, self.season, self.info["episode"]]
        send_rating_for_media_item(media_type="episode",
                                   media_id=identifier,
                                   rating=rating)
        self.update_states()

    @ch.click(6006)
    def open_rating_list(self):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        listitems = get_rated_media_items("tv/episodes")
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        wm.open_video_list(prev_window=self,
                           listitems=listitems)

    def onClick(self, control_id):
        ch.serve(control_id, self)

    def update_states(self, force_update=True):
        if force_update:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, self.account_states = extended_episode_info(tvshow_id=self.tmdb_id,
                                                               season=self.season,
                                                               episode=self.episode_number,
                                                               cache_time=0)
        if not self.account_states:
            return None
        if self.account_states["rated"]:
            self.window.setProperty("movie.rated", str(self.account_states["rated"]["value"]))
        else:
            self.window.setProperty("movie.rated", "")
