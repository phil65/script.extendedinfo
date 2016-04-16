# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcgui

from resources.lib import TheMovieDB as tmdb
from DialogBaseInfo import DialogBaseInfo

from kodi65 import imagetools
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
        TYPE = "Actor"
        LISTS = [(ID_LIST_MOVIE_ROLES, "movie_roles"),
                 (ID_LIST_TV_ROLES, "tvshow_roles"),
                 (ID_LIST_IMAGES, "images"),
                 (ID_LIST_MOVIE_CREW, "movie_crew_roles"),
                 (ID_LIST_TV_CREW, "tvshow_crew_roles"),
                 (ID_LIST_TAGGED_IMAGES, "tagged_images")]

        def __init__(self, *args, **kwargs):
            super(DialogActorInfo, self).__init__(*args, **kwargs)
            self.id = kwargs.get('id', False)
            data = tmdb.extended_actor_info(actor_id=self.id)
            if not data:
                return None
            self.info, self.lists = data
            self.info.update_properties(imagetools.blur(self.info.get_art("thumb")))

        def onInit(self):
            self.get_youtube_vids(self.info.label)
            super(DialogActorInfo, self).onInit()

        def onClick(self, control_id):
            super(DialogActorInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(ID_CONTROL_PLOT)
        def show_plot(self, control_id):
            xbmcgui.Dialog().textviewer(heading=addon.LANG(32037),
                                        text=self.info.get_property("biography"))

    return DialogActorInfo
