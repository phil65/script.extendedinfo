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
            tvdb_id = get_imdb_id_from_db(media_type="tvshow",
                                          dbid=self.dbid)
            if tvdb_id:
                self.tmdb_id = get_show_tmdb_id(tvdb_id)
        elif tvdb_id:
            self.tmdb_id = get_show_tmdb_id(tvdb_id)
        elif imdb_id:
            self.tmdb_id = get_show_tmdb_id(tvdb_id=imdb_id,
                                            source="imdb_id")
        elif self.name:
            self.tmdb_id = search_media(media_name=kwargs.get('name'),
                                        year="",
                                        media_type="tv")
        if self.tmdb_id:
            data = extended_tvshow_info(tvshow_id=self.tmdb_id,
                                        dbid=self.dbid)
            if data:
                self.info, self.data, self.account_states = data
            else:
                notify(LANG(32143))
                return None
            youtube_thread = GetYoutubeVidsThread(search_str=self.info['title'] + " tv",
                                                  hd="",
                                                  order="relevance",
                                                  limit=15)
            youtube_thread.start()
            cert_list = get_certification_list("tv")
            for item in self.data["certifications"]:
                if item["iso_3166_1"] in cert_list:
                    # language = item["iso_3166_1"]
                    rating = item["certification"]
                    language_certs = cert_list[item["iso_3166_1"]]
                    hit = dictfind(lst=language_certs,
                                   key="certification",
                                   value=rating)
                    if hit:
                        item["meaning"] = hit["meaning"]
            if "dbid" not in self.info:  # need to add comparing for tvshows
                poster_thread = FunctionThread(function=get_file,
                                               param=self.info["Poster"])
                poster_thread.start()
            if "dbid" not in self.info:
                poster_thread.join()
                self.info['Poster'] = poster_thread.listitems
            filter_thread = FilterImageThread(image=self.info["Poster"],
                                              radius=25)
            filter_thread.start()
            youtube_thread.join()
            filter_thread.join()
            self.info['ImageFilter'] = filter_thread.image
            self.info['ImageColor'] = filter_thread.imagecolor
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
            notify(LANG(32143))

    def onInit(self):
        super(DialogTVShowInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.info["ImageColor"])
        pass_dict_to_skin(data=self.info,
                          prefix="movie.",
                          window_id=self.window_id)
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
            listitem = self.getControl(control_id).getSelectedItem()
            credit_id = listitem.getProperty("credit_id")
            selection = xbmcgui.Dialog().select(heading=LANG(32151),
                                                list=[LANG(32147), LANG(32009)])
            if selection == 0:
                self.open_credit_dialog(credit_id)
            if selection == 1:
                wm.open_actor_info(prev_window=self,
                                   actor_id=listitem.getProperty("id"))
        elif control_id in [150]:
            wm.open_tvshow_info(prev_window=self,
                                tvshow_id=control.getSelectedItem().getProperty("id"),
                                dbid=control.getSelectedItem().getProperty("dbid"))
        elif control_id in [250]:
            wm.open_season_info(prev_window=self,
                                tvshow_id=self.tmdb_id,
                                season=control.getSelectedItem().getProperty("season"),
                                tvshow=self.info['title'])
        elif control_id in [350, 1150]:
            PLAYER.play_youtube_video(youtube_id=control.getSelectedItem().getProperty("youtube_id"),
                                      listitem=control.getSelectedItem(),
                                      window=self)
        elif control_id == 550:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = get_company_data(control.getSelectedItem().getProperty("id"))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            wm.open_video_list(prev_window=self,
                               listitems=listitems)
        elif control_id == 950:
            filters = [{"id": control.getSelectedItem().getProperty("id"),
                        "type": "with_keywords",
                        "typelabel": LANG(32114),
                        "label": control.getSelectedItem().getLabel()}]
            wm.open_video_list(prev_window=self,
                               filters=filters)
        elif control_id == 850:
            filters = [{"id": control.getSelectedItem().getProperty("id"),
                        "type": "with_genres",
                        "typelabel": LANG(135),
                        "label": control.getSelectedItem().getLabel()}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")
        elif control_id in [1250, 1350]:
            wm.open_slideshow(image=control.getSelectedItem().getProperty("original"))
        elif control_id == 1450:
            filters = [{"id": control.getSelectedItem().getProperty("id"),
                        "type": "with_networks",
                        "typelabel": LANG(32152),
                        "label": control.getSelectedItem().getLabel()}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")
        elif control_id == 445:
            self.show_manage_dialog()
        elif control_id == 6001:
            rating = get_rating_from_user()
            if rating:
                send_rating_for_media_item(media_type="tv",
                                           media_id=self.tmdb_id,
                                           rating=rating)
                self.update_states()
        elif control_id == 6002:
            listitems = [LANG(32144), LANG(32145)]
            index = xbmcgui.Dialog().select(heading=LANG(32136),
                                            list=listitems)
            if index == -1:
                pass
            elif index == 0:
                wm.open_video_list(prev_window=self,
                                   media_type="tv",
                                   mode="favorites")
            elif index == 1:
                wm.open_video_list(prev_window=self,
                                   mode="rating",
                                   media_type="tv")
        elif control_id == 6003:
            change_fav_status(self.info["id"], "tv", "true")
            self.update_states()
        elif control_id == 6006:
            wm.open_video_list(prev_window=self,
                               mode="rating",
                               media_type="tv")
        elif control_id == 132:
            wm.open_textviewer(header=LANG(32037),
                               text=self.info["Plot"],
                               color=self.info['ImageColor'])

    def update_states(self, forceupdate=True):
        if forceupdate:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, updated_state = extended_tvshow_info(tvshow_id=self.tmdb_id,
                                                        cache_time=0,
                                                        dbid=self.dbid)
            self.account_states = updated_state
        if self.account_states:
            if self.account_states["favorite"]:
                self.window.setProperty("FavButton_Label", LANG(32155))
                self.window.setProperty("movie.favorite", "True")
            else:
                self.window.setProperty("FavButton_Label", LANG(32154))
                self.window.setProperty("movie.favorite", "")
            if self.account_states["rated"]:
                self.window.setProperty("movie.rated", str(self.account_states["rated"]["value"]))
            else:
                self.window.setProperty("movie.rated", "")
            self.window.setProperty("movie.watchlist", str(self.account_states["watchlist"]))

    def show_manage_dialog(self):
        manage_list = []
        title = self.info.get("TVShowTitle", "")
        # imdb_id = str(self.info.get("imdb_id", ""))
        # filename = self.info.get("FilenameAndPath", False)
        if self.dbid:
            manage_list += [[LANG(413), "RunScript(script.artwork.downloader,mode=gui,mediatype=tv,dbid=" + self.dbid + ")"],
                            [LANG(14061), "RunScript(script.artwork.downloader, mediatype=tv, dbid=" + self.dbid + ")"],
                            [LANG(32101), "RunScript(script.artwork.downloader,mode=custom,mediatype=tv,dbid=" + self.dbid + ",extrathumbs)"],
                            [LANG(32100), "RunScript(script.artwork.downloader,mode=custom,mediatype=tv,dbid=" + self.dbid + ")"]]
        else:
            manage_list += [[LANG(32166), "RunScript(special://home/addons/plugin.program.sickbeard/resources/lib/addshow.py," + title + ")"]]
        # if xbmc.getCondVisibility("system.hasaddon(script.tvtunes)") and self.dbid:
        #     manage_list.append([LANG(32102), "RunScript(script.tvtunes,mode=solo&amp;tvpath=$ESCINFO[Window.Property(movie.FilenameAndPath)]&amp;tvname=$INFO[Window.Property(movie.TVShowTitle)])"])
        if xbmc.getCondVisibility("system.hasaddon(script.libraryeditor)") and self.dbid:
            manage_list.append([LANG(32103), "RunScript(script.libraryeditor,DBID=" + self.dbid + ")"])
        manage_list.append([LANG(1049), "Addon.OpenSettings(script.extendedinfo)"])
        listitems = [item[0] for item in manage_list]
        selection = xbmcgui.Dialog().select(heading=LANG(32133),
                                            list=listitems)
        if selection < 0:
            return None
        builtin_list = manage_list[selection][1].split("||")
        for item in builtin_list:
            xbmc.executebuiltin(item)
