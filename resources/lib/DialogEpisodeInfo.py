# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
from ImageTools import *
from BaseClasses import DialogBaseInfo
from WindowManager import wm


class DialogEpisodeInfo(DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
        self.tmdb_id = kwargs.get('show_id')
        self.season = kwargs.get('season')
        self.showname = kwargs.get('tvshow')
        self.episodenumber = kwargs.get('episode')
        if self.tmdb_id or self.showname:
            self.data = extended_episode_info(self.tmdb_id, self.season, self.episodenumber)
            if not self.data:
                return
            # prettyprint(self.data)
            search_string = "%s tv" % (self.data["general"]['title'])
            youtube_thread = GetYoutubeVidsThread(search_string, "", "relevance", 15)
            youtube_thread.start()
            if "dbid" not in self.data["general"]:  # need to add comparing for episodes
                poster_thread = FunctionThread(get_file, self.data["general"]["Poster"])
                poster_thread.start()
            if "dbid" not in self.data["general"]:
                poster_thread.join()
                self.data["general"]['Poster'] = poster_thread.listitems
            filter_thread = FilterImageThread(self.data["general"]["Poster"], 25)
            filter_thread.start()
            youtube_thread.join()
            filter_thread.join()
            self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
            self.listitems = [(1000, create_listitems(self.data["actors"] + self.data["guest_stars"], 0)),
                              (750, create_listitems(self.data["crew"], 0)),
                              (1150, create_listitems(self.data["videos"], 0)),
                              # (1250, create_listitems(self.data["guest_stars"], 0)),
                              (1350, create_listitems(self.data["images"], 0)),
                              (350, create_listitems(youtube_thread.listitems, 0))]
        else:
            notify(ADDON.getLocalizedString(32143))

    def onInit(self):
        super(DialogEpisodeInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        self.window.setProperty("type", "Episode")
        pass_dict_to_skin(self.data["general"], "movie.", False, False, self.window_id)
        self.fill_lists()

    def onClick(self, control_id):
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if control_id in [1000, 750]:
            actor_id = self.getControl(control_id).getSelectedItem().getProperty("id")
            credit_id = self.getControl(control_id).getSelectedItem().getProperty("credit_id")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, credit_id=credit_id)
            dialog.doModal()
        elif control_id in [350, 1150]:
            listitem = self.getControl(control_id).getSelectedItem()
            PLAYER.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, window=self)
        elif control_id in [1250, 1350]:
            image = self.getControl(control_id).getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif control_id == 132:
            w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=self.season["general"]["Plot"], color=self.season["general"]['ImageColor'])
            w.doModal()
        elif control_id == 6001:
            rating = get_rating_from_user()
            if rating:
                identifier = [self.tmdb_id, self.season, self.data["general"]["episode"]]
                send_rating_for_media_item("episode", identifier, rating)
                self.update_states()
        elif control_id == 6006:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = get_rated_media_items("tv/episodes")
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.open_video_list(listitems=listitems)

    def update_states(self, forceupdate=True):
        if forceupdate:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            self.update = extended_episode_info(self.tmdb_id, self.season, self.episodenumber, 0)
            self.data["account_states"] = self.update["account_states"]
        if self.data["account_states"]:
            # if self.data["account_states"]["favorite"]:
            #     self.window.setProperty("FavButton_Label", "UnStar episode")
            #     self.window.setProperty("movie.favorite", "True")
            # else:
            #     self.window.setProperty("FavButton_Label", "Star episode")
            #     self.window.setProperty("movie.favorite", "")
            if self.data["account_states"]["rated"]:
                self.window.setProperty("movie.rated", str(self.data["account_states"]["rated"]["value"]))
            else:
                self.window.setProperty("movie.rated", "")
            # self.window.setProperty("movie.watchlist", str(self.data["account_states"]["watchlist"]))
            # notify(str(self.data["account_states"]["rated"]["value"]))
