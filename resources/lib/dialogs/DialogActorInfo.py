# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcgui

from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB as tmdb
from resources.lib.WindowManager import wm
from DialogBaseInfo import DialogBaseInfo

from kodi65 import addon
from ActionHandler import ActionHandler

ID_LIST_MOVIE_ROLES = 150
ID_LIST_TV_ROLES = 250
ID_LIST_YOUTUBE = 350
ID_LIST_IMAGES = 450
ID_LIST_MOVIE_CREW = 550
ID_LIST_TV_CREW = 650
ID_LIST_TAGGED_IMAGES = 750
ID_LIST_BACKDROPS = 1350
ID_CONTROL_PLOT = 132

ch = ActionHandler()


def get_window(window_type):

    class DialogActorInfo(DialogBaseInfo, window_type):

        def __init__(self, *args, **kwargs):
            super(DialogActorInfo, self).__init__(*args, **kwargs)
            self.id = kwargs.get('id', False)
            self.type = "Actor"
            data = tmdb.extended_actor_info(actor_id=self.id)
            if not data:
                return None
            self.info, self.data = data
            self.info.update_properties(ImageTools.blur(self.info.get("thumb")))
            self.listitems = [(ID_LIST_MOVIE_ROLES, Utils.merge_dict_lists(self.data["movie_roles"], "character")),
                              (ID_LIST_TV_ROLES, Utils.merge_dict_lists(self.data["tvshow_roles"], "character")),
                              (ID_LIST_IMAGES, self.data["images"]),
                              (ID_LIST_MOVIE_CREW, Utils.merge_dict_lists(self.data["movie_crew_roles"])),
                              (ID_LIST_TV_CREW, Utils.merge_dict_lists(self.data["tvshow_crew_roles"])),
                              (ID_LIST_TAGGED_IMAGES, self.data["tagged_images"])]

        def onInit(self):
            self.get_youtube_vids(self.info.label)
            super(DialogActorInfo, self).onInit()

        def onClick(self, control_id):
            super(DialogActorInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        def onAction(self, action):
            super(DialogActorInfo, self).onAction(action)
            ch.serve_action(action, self.getFocusId(), self)

        @ch.context("tvshow")
        @ch.click_by_type("tvshow")
        def open_tvshow_dialog(self, control_id):
            selection = xbmcgui.Dialog().contextmenu(list=[addon.LANG(32148), addon.LANG(32147)])
            if selection == 0:
                wm.open_tvshow_info(prev_window=self,
                                    tmdb_id=self.FocusedItem(control_id).getProperty("id"),
                                    dbid=self.FocusedItem(control_id).getProperty("dbid"))
            if selection == 1:
                self.open_credit_dialog(credit_id=self.FocusedItem(control_id).getProperty("credit_id"))

        @ch.click(ID_LIST_IMAGES)
        @ch.click(ID_LIST_TAGGED_IMAGES)
        def open_image(self, control_id):
            listitems = next((v for (i, v) in self.listitems if i == control_id), None)
            pos = wm.open_slideshow(listitems=listitems,
                                    index=self.getControl(control_id).getSelectedPosition())
            self.getControl(control_id).selectItem(pos)

        @ch.click(ID_CONTROL_PLOT)
        def show_plot(self, control_id):
            xbmcgui.Dialog().textviewer(heading=addon.LANG(32037),
                                        text=self.info.get_property("biography"))

    return DialogActorInfo
