# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from ImageTools import *
from TheMovieDB import *
from YouTube import *
from BaseClasses import DialogBaseInfo
from WindowManager import wm
import VideoPlayer
PLAYER = VideoPlayer.VideoPlayer()


class DialogActorInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogActorInfo, self).__init__(*args, **kwargs)
        self.id = kwargs.get('id', False)
        if not self.id:
            name = kwargs.get('name').decode("utf-8").split(" " + LANG(20347) + " ")
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
            self.id = get_person_info(name)
            if self.id:
                self.id = self.id["id"]
            else:
                return None
        if not self.id:
            notify(LANG(32143))
            return None
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        data = extended_actor_info(actor_id=self.id)
        if data:
            self.info, self.data = data
        else:
            notify(LANG(32143))
            return None
        youtube_thread = GetYoutubeVidsThread(search_str=self.info["name"],
                                              limit=15)
        youtube_thread.start()
        filter_thread = FilterImageThread(image=self.info["thumb"],
                                          radius=25)
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
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        super(DialogActorInfo, self).onInit()
        HOME.setProperty("actor.ImageColor", self.info["ImageColor"])
        pass_dict_to_skin(data=self.info,
                          prefix="actor.",
                          window_id=self.window_id)
        self.fill_lists()

    def onClick(self, control_id):
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(ActorInfo.ImageColor)"))
        control = self.getControl(control_id)
        if control_id in [150, 550]:
            wm.open_movie_info(prev_window=self,
                               movie_id=control.getSelectedItem().getProperty("id"),
                               dbid=control.getSelectedItem().getProperty("dbid"))
        elif control_id in [250, 650]:
            selection = xbmcgui.Dialog().select(heading=LANG(32151),
                                                list=[LANG(32147), LANG(32148)])
            if selection == 0:
                self.open_credit_dialog(credit_id=control.getSelectedItem().getProperty("credit_id"))
            if selection == 1:
                wm.open_tvshow_info(prev_window=self,
                                    tvshow_id=control.getSelectedItem().getProperty("id"),
                                    dbid=control.getSelectedItem().getProperty("dbid"))
        elif control_id in [450, 750]:
            wm.open_slideshow(image=control.getSelectedItem().getProperty("original"))
        elif control_id == 350:
            PLAYER.play_youtube_video(youtube_id=control.getSelectedItem().getProperty("youtube_id"),
                                      listitem=control.getSelectedItem(),
                                      window=self)
        elif control_id == 132:
            wm.open_textviewer(header=LANG(32037),
                               text=self.info["biography"],
                               color=self.info['ImageColor'])
