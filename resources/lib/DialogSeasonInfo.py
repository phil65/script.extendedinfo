# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogEpisodeInfo
from ImageTools import *
from BaseClasses import DialogBaseInfo
from WindowManager import wm

class DialogSeasonInfo(DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogSeasonInfo, self).__init__(*args, **kwargs)
        self.tmdb_id = kwargs.get('id')
        self.season = kwargs.get('season')
        self.tvshow = kwargs.get('tvshow')
        if self.tmdb_id or (self.season and self.tvshow):
            self.data = extended_season_info(self.tmdb_id, self.tvshow, self.season)
            if not self.data:
                return
            search_string = "%s %s tv" % (self.data["general"]["TVShowTitle"], self.data["general"]['title'])
            youtube_thread = GetYoutubeVidsThread(search_string, "", "relevance", 15)
            youtube_thread.start()
            if "dbid" not in self.data["general"]:  # need to add comparing for seasons
                self.data["general"]['Poster'] = get_file(self.data["general"]["Poster"])
            filter_thread = FilterImageThread(self.data["general"]["Poster"], 25)
            filter_thread.start()
            youtube_thread.join()
            filter_thread.join()
            self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
            self.listitems = [(1000, create_listitems(self.data["actors"], 0)),
                              (750, create_listitems(self.data["crew"], 0)),
                              (2000, create_listitems(self.data["episodes"], 0)),
                              (1150, create_listitems(self.data["videos"], 0)),
                              (1250, create_listitems(self.data["images"], 0)),
                              (1350, create_listitems(self.data["backdrops"], 0)),
                              (350, create_listitems(youtube_thread.listitems, 0))]
        else:
            notify(ADDON.getLocalizedString(32143))

    def onInit(self):
        super(DialogSeasonInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        self.window.setProperty("type", "season")
        pass_dict_to_skin(self.data["general"], "movie.", False, False, self.window_id)
        self.fill_lists()

    def onClick(self, control_id):
        control = self.getControl(control_id)
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if control_id in [1000, 750]:
            actor_id = control.getSelectedItem().getProperty("id")
            credit_id = control.getSelectedItem().getProperty("credit_id")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, credit_id=credit_id)
            dialog.doModal()
        elif control_id in [2000]:
            episode = control.getSelectedItem().getProperty("episode")
            season = control.getSelectedItem().getProperty("season")
            if not self.tmdb_id:
                response = get_tmdb_data("search/tv?query=%s&language=%s&" % (urllib.quote_plus(self.tvshow), ADDON.getSetting("LanguageID")), 30)
                self.tmdb_id = str(response['results'][0]['id'])
            wm.add_to_stack(self)
            self.close()
            dialog = DialogEpisodeInfo.DialogEpisodeInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, show_id=self.tmdb_id, season=season, episode=episode)
            dialog.doModal()
        elif control_id in [350, 1150]:
            listitem = control.getSelectedItem()
            PLAYER.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, window=self)
        elif control_id in [1250, 1350]:
            image = control.getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif control_id == 132:
            w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=self.data["general"]["Plot"], color=self.data["general"]['ImageColor'])
            w.doModal()
