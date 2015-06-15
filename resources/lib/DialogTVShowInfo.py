# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from local_db import get_imdb_id_from_db
from ImageTools import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogSeasonInfo
from BaseClasses import DialogBaseInfo
from WindowManager import wm

class DialogTVShowInfo(DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogTVShowInfo, self).__init__(*args, **kwargs)
        self.tmdb_id = None
        tmdb_id = kwargs.get('id', False)
        imdb_id = kwargs.get('imdb_id')
        tvdb_id = kwargs.get('tvdb_id')
        self.name = kwargs.get('name')
        if tmdb_id:
            self.tmdb_id = tmdb_id
        elif self.dbid and (int(self.dbid) > 0):
            tvdb_id = get_imdb_id_from_db("tvshow", self.dbid)
            if tvdb_id:
                self.tmdb_id = get_show_tmdb_id(tvdb_id)
        elif tvdb_id:
            self.tmdb_id = get_show_tmdb_id(tvdb_id)
        elif imdb_id:
            self.tmdb_id = get_show_tmdb_id(imdb_id, "imdb_id")
        elif self.name:
            self.tmdb_id = search_media(kwargs.get('name'), "", "tv")
        if self.tmdb_id:
            self.data = extended_tvshow_info(self.tmdb_id, dbid=self.dbid)
            if not self.data:
                return None
            youtube_thread = GetYoutubeVidsThread(self.data["general"]['title'] + " tv", "", "relevance", 15)
            youtube_thread.start()
            cert_list = get_certification_list("tv")
            for item in self.data["certifications"]:
                if item["iso_3166_1"] in cert_list:
                    # language = item["iso_3166_1"]
                    rating = item["certification"]
                    language_certs = cert_list[item["iso_3166_1"]]
                    hit = dictfind(language_certs, "certification", rating)
                    if hit:
                        item["meaning"] = hit["meaning"]
            if "dbid" not in self.data["general"]:  # need to add comparing for tvshows
                # notify("download Poster")
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
            self.listitems = [(150, create_listitems(self.data["similar"], 0)),
                              (250, create_listitems(self.data["seasons"], 0)),
                              (1450, create_listitems(self.data["networks"], 0)),
                              (550, create_listitems(self.data["studios"], 0)),
                              (650, create_listitems(self.data["certifications"], 0)),
                              (750, create_listitems(self.data["crew"], 0)),
                              (850, create_listitems(self.data["genres"], 0)),
                              (950, create_listitems(self.data["keywords"], 0)),
                              (1000, create_listitems(self.data["actors"], 0)),
                              (1150, create_listitems(self.data["videos"], 0)),
                              (1250, create_listitems(self.data["images"], 0)),
                              (1350, create_listitems(self.data["backdrops"], 0)),
                              (350, create_listitems(youtube_thread.listitems, 0))]
        else:
            notify(ADDON.getLocalizedString(32143))

    def onInit(self):
        super(DialogTVShowInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        pass_dict_to_skin(self.data["general"], "movie.", False, False, self.window_id)
        self.window.setProperty("type", "TVShow")
        self.fill_lists()
        self.update_states(False)

    def onClick(self, control_id):
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        control = self.getControl(control_id)
        if control_id == 120:
            self.close()
            xbmc.executebuiltin("ActivateWindow(videos,videodb://tvshows/titles/%s/)" % (self.dbid))
        elif control_id in [1000, 750]:
            actor_id = control.getSelectedItem().getProperty("id")
            credit_id = control.getSelectedItem().getProperty("credit_id")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, credit_id=credit_id)
            dialog.doModal()
        elif control_id in [150]:
            tmdb_id = control.getSelectedItem().getProperty("id")
            dbid = control.getSelectedItem().getProperty("dbid")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=tmdb_id, dbid=dbid)
            dialog.doModal()
        elif control_id in [250]:
            season = control.getSelectedItem().getProperty("season")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogSeasonInfo.DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=self.tmdb_id, season=season, tvshow=self.data["general"]['title'])
            dialog.doModal()
        elif control_id in [350, 1150]:
            listitem = control.getSelectedItem()
            PLAYER.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, window=self)
        elif control_id == 550:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = get_company_data(control.getSelectedItem().getProperty("id"))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.open_video_list(listitems=listitems)
            # xbmc.executebuiltin("ActivateWindow(busydialog)")
            # filters = {"with_networks": control.getSelectedItem().getProperty("id")}
            # listitems = get_company_data(control.getSelectedItem().getProperty("id"))
            # xbmc.executebuiltin("Dialog.Close(busydialog)")
            # self.open_video_list(filters=filters, media_type="tv")
        elif control_id == 950:
            keyword_id = control.getSelectedItem().getProperty("id")
            keyword_name = control.getSelectedItem().getLabel()
            filters = [{"id": keyword_id,
                        "type": "with_keywords",
                        "typelabel": ADDON.getLocalizedString(32114),
                        "label": keyword_name}]
            self.open_video_list(filters=filters)
        elif control_id == 850:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            genreid = control.getSelectedItem().getProperty("id")
            genrename = control.getSelectedItem().getLabel()
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            filters = [{"id": genreid,
                        "type": "with_genres",
                        "typelabel": xbmc.getLocalizedString(135),
                        "label": genrename}]
            self.open_video_list(filters=filters, media_type="tv")
        elif control_id in [1250, 1350]:
            image = control.getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif control_id == 1450:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            company_id = control.getSelectedItem().getProperty("id")
            company_name = control.getSelectedItem().getLabel()
            filters = [{"id": company_id,
                        "type": "with_networks",
                        "typelabel": ADDON.getLocalizedString(32152),
                        "label": company_name}]
            listitems = get_company_data(company_id)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.open_video_list(filters=filters, media_type="tv")
        elif control_id == 445:
            self.show_manage_dialog()
        elif control_id == 6001:
            rating = get_rating_from_user()
            if rating:
                send_rating_for_media_item("tv", self.tmdb_id, rating)
                self.update_states()
        elif control_id == 6002:
            listitems = [ADDON.getLocalizedString(32144), ADDON.getLocalizedString(32145)]
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
            if index == -1:
                pass
            elif index == 0:
                self.open_video_list(media_type="tv", mode="favorites")
            elif index == 1:
                self.open_video_list(mode="rating", media_type="tv")
        elif control_id == 6003:
            change_fav_status(self.data["general"]["id"], "tv", "true")
            self.update_states()
        elif control_id == 6006:
            self.open_video_list(mode="rating", media_type="tv")
        elif control_id == 132:
            w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=self.data["general"]["Plot"], color=self.data["general"]['ImageColor'])
            w.doModal()
        # elif control_id == 650:
        #     xbmc.executebuiltin("ActivateWindow(busydialog)")
        #     country = control.getSelectedItem().getProperty("iso_3166_1")
        #     certification = self.getControl(control_id).getSelectedItem().getProperty("certification")
        #     listitems = GetMoviesWithCertification(country, certification)
        #     xbmc.executebuiltin("Dialog.Close(busydialog)")
        #     self.open_video_list(listitems=listitems)
        # elif control_id == 450:
        #     xbmc.executebuiltin("ActivateWindow(busydialog)")
        #     listitems = get_movies_from_list(self.getControl(control_id).getSelectedItem().getProperty("id"))
        #     xbmc.executebuiltin("Dialog.Close(busydialog)")
        #     self.open_video_list(listitems=listitems)

    def update_states(self, forceupdate=True):
        if forceupdate:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            self.update = extended_tvshow_info(self.tmdb_id, 0, dbid=self.dbid)
            self.data["account_states"] = self.update["account_states"]
        if self.data["account_states"]:
            if self.data["account_states"]["favorite"]:
                self.window.setProperty("FavButton_Label", ADDON.getLocalizedString(32155))
                self.window.setProperty("movie.favorite", "True")
            else:
                self.window.setProperty("FavButton_Label", ADDON.getLocalizedString(32154))
                self.window.setProperty("movie.favorite", "")
            if self.data["account_states"]["rated"]:
                self.window.setProperty("movie.rated", str(self.data["account_states"]["rated"]["value"]))
            else:
                self.window.setProperty("movie.rated", "")
            self.window.setProperty("movie.watchlist", str(self.data["account_states"]["watchlist"]))
            # notify(str(self.data["account_states"]["rated"]["value"]))

    def show_manage_dialog(self):
        manage_list = []
        title = self.data["general"].get("TVShowTitle", "")
        # imdb_id = str(self.data["general"].get("imdb_id", ""))
        # filename = self.data["general"].get("FilenameAndPath", False)
        if self.dbid:
            manage_list += [[xbmc.getLocalizedString(413), "RunScript(script.artwork.downloader,mode=gui,mediatype=tv,dbid=" + self.dbid + ")"],
                            [xbmc.getLocalizedString(14061), "RunScript(script.artwork.downloader, mediatype=tv, dbid=" + self.dbid + ")"],
                            [ADDON.getLocalizedString(32101), "RunScript(script.artwork.downloader,mode=custom,mediatype=tv,dbid=" + self.dbid + ",extrathumbs)"],
                            [ADDON.getLocalizedString(32100), "RunScript(script.artwork.downloader,mode=custom,mediatype=tv,dbid=" + self.dbid + ")"]]
        else:
            manage_list += [[ADDON.getLocalizedString(32166), "RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/addshow.py," + title + ")"]]
        # if xbmc.getCondVisibility("system.hasaddon(script.tvtunes)") and self.dbid:
        #     manage_list.append([ADDON.getLocalizedString(32102), "RunScript(script.tvtunes,mode=solo&amp;tvpath=$ESCINFO[Window.Property(movie.FilenameAndPath)]&amp;tvname=$INFO[Window.Property(movie.TVShowTitle)])"])
        if xbmc.getCondVisibility("system.hasaddon(script.libraryeditor)") and self.dbid:
            manage_list.append([ADDON.getLocalizedString(32103), "RunScript(script.libraryeditor,DBID=" + self.dbid + ")"])
        manage_list.append([xbmc.getLocalizedString(1049), "Addon.OpenSettings(script.extendedinfo)"])
        listitems = [item[0] for item in manage_list]
        selection = xbmcgui.Dialog().select(ADDON.getLocalizedString(32133), listitems)
        if selection > -1:
            builtin_list = manage_list[selection][1].split("||")
            for item in builtin_list:
                xbmc.executebuiltin(item)
