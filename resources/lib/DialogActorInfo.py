# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from ImageTools import *
from TheMovieDB import *
from YouTube import *
import DialogVideoInfo
import DialogTVShowInfo
from BaseClasses import DialogBaseInfo
from WindowManager import wm


class DialogActorInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogActorInfo, self).__init__(*args, **kwargs)
        self.id = kwargs.get('id', False)
        if not self.id:
            name = kwargs.get('name').decode("utf-8").split(" " + xbmc.getLocalizedString(20347) + " ")
            names = name[0].strip().split(" / ")
            if len(names) > 1:
                ret = xbmcgui.Dialog().select(ADDON.getLocalizedString(32027), names)
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
            notify(ADDON.getLocalizedString(32143))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            return None
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.data = extended_actor_info(self.id)
        youtube_thread = GetYoutubeVidsThread(self.data["general"]["name"], "", "relevance", 15)
        youtube_thread.start()
        filter_thread = FilterImageThread(self.data["general"]["thumb"], 25)
        filter_thread.start()
        db_movies = len([item for item in self.data["movie_roles"] if "dbid" in item])
        self.data["general"]["DBMovies"] = str(db_movies)
        movie_crew_roles = self.merge_person_listitems(self.data["movie_crew_roles"])
        tvshow_crew_roles = self.merge_person_listitems(self.data["tvshow_crew_roles"])
        filter_thread.join()
        self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
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
        HOME.setProperty("actor.ImageColor", self.data["general"]["ImageColor"])
        pass_dict_to_skin(self.data["general"], "actor.", False, False, self.window_id)
        self.fill_lists()

    def onClick(self, control_id):
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(ActorInfo.ImageColor)"))
        if control_id in [150, 550]:
            listitem = self.getControl(control_id).getSelectedItem()
            wm.add_to_stack(self)
            self.close()
            dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=listitem.getProperty("id"), dbid=listitem.getProperty("dbid"))
            dialog.doModal()
        elif control_id in [250, 650]:
            listitem = self.getControl(control_id).getSelectedItem()
            options = [ADDON.getLocalizedString(32147), ADDON.getLocalizedString(32148)]
            selection = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), options)
            if selection == 0:
                info = get_credit_info(listitem.getProperty("credit_id"))
                listitems = handle_tmdb_seasons(info["media"]["seasons"])
                listitems += handle_tmdb_episodes(info["media"]["episodes"])
                if not listitems:
                    listitems += [{"label": xbmc.getLocalizedString(19055)}]
                w = SelectDialog('DialogSelect.xml', ADDON_PATH, listing=create_listitems(listitems))
                w.doModal()
                if w.type == "episode":
                    import DialogEpisodeInfo
                    wm.add_to_stack(self)
                    self.close()
                    dialog = DialogEpisodeInfo.DialogEpisodeInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, season=listitems[w.index]["season"], episode=listitems[w.index]["episode"], show_id=listitem.getProperty("id"))
                    dialog.doModal()
                elif w.type == "season":
                    import DialogSeasonInfo
                    wm.add_to_stack(self)
                    self.close()
                    dialog = DialogSeasonInfo.DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, season=listitems[w.index]["season"], tvshow=listitem.getLabel())
                    dialog.doModal()
            if selection == 1:
                wm.add_to_stack(self)
                self.close()
                dialog = DialogTVShowInfo.DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=listitem.getProperty("id"), dbid=listitem.getProperty("dbid"))
                dialog.doModal()
        elif control_id in [450, 750]:
            image = self.getControl(control_id).getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif control_id == 350:
            listitem = self.getControl(control_id).getSelectedItem()
            PLAYER.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, window=self)
        elif control_id == 132:
            text = self.data["general"]["biography"]
            w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=text, color=self.data["general"]['ImageColor'])
            w.doModal()
