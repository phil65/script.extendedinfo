# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
from omdb import *
import DialogActorInfo
from ImageTools import *
import threading
from BaseClasses import DialogBaseInfo
from WindowManager import wm


class DialogVideoInfo(DialogBaseInfo):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogVideoInfo, self).__init__(*args, **kwargs)
        if not ADDON.getSetting("first_start_infodialog"):
            ADDON.setSetting("first_start_infodialog", "True")
            xbmcgui.Dialog().ok(ADDON_NAME, ADDON.getLocalizedString(32140), ADDON.getLocalizedString(32141))
        self.monitor = SettingsMonitor()
        tmdb_id = kwargs.get('id')
        imdb_id = kwargs.get('imdb_id')
        self.name = kwargs.get('name')
        if tmdb_id:
            self.tmdb_id = tmdb_id
        else:
            self.tmdb_id = get_movie_tmdb_id(imdb_id=imdb_id, dbid=self.dbid, name=self.name)
        if not self.tmdb_id:
            notify(ADDON.getLocalizedString(32143))
            return None
        self.close()
        self.data = extended_movie_info(self.tmdb_id, self.dbid)
        if "general" not in self.data:
            return None
        log("Blur image %s with radius %i" % (self.data["general"]["thumb"], 25))
        youtube_thread = GetYoutubeVidsThread(self.data["general"]["Label"] + " " + self.data["general"]["year"] + ", movie", "", "relevance", 15)
        sets_thread = SetItemsThread(self.data["general"]["SetId"])
        self.omdb_thread = FunctionThread(get_omdb_movie_info, self.data["general"]["imdb_id"])
        lists_thread = FunctionThread(self.sort_lists, self.data["lists"])
        self.omdb_thread.start()
        sets_thread.start()
        youtube_thread.start()
        lists_thread.start()
        vid_id_list = [item["key"] for item in self.data["videos"]]
        crew_list = self.merge_person_listitems(self.data["crew"])
        if "dbid" not in self.data["general"]:
            self.data["general"]['Poster'] = get_file(self.data["general"]["Poster"])
        filter_thread = FilterImageThread(self.data["general"]["thumb"], 25)
        filter_thread.start()
        lists_thread.join()
        self.data["lists"] = lists_thread.listitems
        sets_thread.join()
        cert_list = get_certification_list("movie")
        for item in self.data["releases"]:
            if item["iso_3166_1"] in cert_list:
                language = item["iso_3166_1"]
                certification = item["certification"]
                language_certs = cert_list[language]
                hit = dictfind(language_certs, "certification", certification)
                if hit:
                    item["meaning"] = hit["meaning"]
        self.set_listitems = sets_thread.listitems
        self.setinfo = sets_thread.setinfo
        id_list = sets_thread.id_list
        self.data["similar"] = [item for item in self.data["similar"] if item["id"] not in id_list]
        youtube_thread.join()
        youtube_vids = [item for item in youtube_thread.listitems if item["youtube_id"] not in vid_id_list]
        filter_thread.join()
        self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
        self.listitems = [(1000, create_listitems(self.data["actors"], 0)),
                          (150, create_listitems(self.data["similar"], 0)),
                          (250, create_listitems(self.set_listitems, 0)),
                          (450, create_listitems(self.data["lists"], 0)),
                          (550, create_listitems(self.data["studios"], 0)),
                          (650, create_listitems(self.data["releases"], 0)),
                          (750, create_listitems(crew_list, 0)),
                          (850, create_listitems(self.data["genres"], 0)),
                          (950, create_listitems(self.data["keywords"], 0)),
                          (1050, create_listitems(self.data["reviews"], 0)),
                          (1150, create_listitems(self.data["videos"], 0)),
                          (1250, create_listitems(self.data["images"], 0)),
                          (1350, create_listitems(self.data["backdrops"], 0)),
                          (350, create_listitems(youtube_vids, 0))]

    def onInit(self):
        super(DialogVideoInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        self.window.setProperty("type", "Movie")
        pass_dict_to_skin(self.data["general"], "movie.", False, False, self.window_id)
        self.fill_lists()
        pass_dict_to_skin(self.setinfo, "movie.set.", False, False, self.window_id)
        self.update_states(False)
        self.join_omdb = JoinOmdbThread(self.omdb_thread, self.window_id)
        self.join_omdb.start()

    def onAction(self, action):
        super(DialogVideoInfo, self).onAction(action)

    def onClick(self, control_id):
        control = self.getControl(control_id)
        if control_id in [1000, 750]:
            actor_id = control.getSelectedItem().getProperty("id")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id)
            dialog.doModal()
        elif control_id in [150, 250]:
            movie_id = control.getSelectedItem().getProperty("id")
            dbid = control.getSelectedItem().getProperty("dbid")
            wm.add_to_stack(self)
            self.close()
            dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=movie_id, dbid=dbid)
            dialog.doModal()
        elif control_id in [1250, 1350]:
            image = control.getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif control_id in [350, 1150, 10]:
            listitem = xbmcgui.ListItem(xbmc.getLocalizedString(20410))
            listitem.setInfo('video', {'title': xbmc.getLocalizedString(20410), 'Genre': 'Youtube Video'})
            if control_id == 10:
                youtube_id = self.getControl(1150).getListItem(0).getProperty("youtube_id")
            else:
                youtube_id = control.getSelectedItem().getProperty("youtube_id")
            if youtube_id:
                PLAYER.playYoutubeVideo(youtube_id, control.getSelectedItem(), window=self)
            else:
                notify(ADDON.getLocalizedString(32052))
        elif control_id == 550:
            company_id = control.getSelectedItem().getProperty("id")
            company_name = control.getSelectedItem().getLabel()
            filters = [{"id": company_id,
                        "type": "with_companies",
                        "typelabel": xbmc.getLocalizedString(20388),
                        "label": company_name}]
            self.open_video_list(filters=filters)
        elif control_id == 1050:
            author = control.getSelectedItem().getProperty("author")
            text = "[B]" + author + "[/B][CR]" + clean_text(control.getSelectedItem().getProperty("content"))
            w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH, header=xbmc.getLocalizedString(207), text=text, color=self.data["general"]['ImageColor'])
            w.doModal()
        elif control_id == 950:
            keyword_id = control.getSelectedItem().getProperty("id")
            keyword_name = control.getSelectedItem().getLabel()
            filters = [{"id": keyword_id,
                        "type": "with_keywords",
                        "typelabel": ADDON.getLocalizedString(32114),
                        "label": keyword_name}]
            self.open_video_list(filters=filters)
        elif control_id == 850:
            genre_id = control.getSelectedItem().getProperty("id")
            genre_name = control.getSelectedItem().getLabel()
            filters = [{"id": genre_id,
                        "type": "with_genres",
                        "typelabel": xbmc.getLocalizedString(135),
                        "label": genre_name}]
            self.open_video_list(filters=filters)
        elif control_id == 650:
            country = control.getSelectedItem().getProperty("iso_3166_1")
            certification = control.getSelectedItem().getProperty("certification")
            year = control.getSelectedItem().getProperty("year")
            filters = [{"id": country,
                        "type": "certification_country",
                        "typelabel": ADDON.getLocalizedString(32153),
                        "label": country},
                       {"id": certification,
                        "type": "certification",
                        "typelabel": ADDON.getLocalizedString(32127),
                        "label": certification},
                       {"id": year,
                        "type": "year",
                        "typelabel": xbmc.getLocalizedString(345),
                        "label": year}]
            self.open_video_list(filters=filters)
        elif control_id == 450:
            list_id = control.getSelectedItem().getProperty("id")
            list_title = control.getSelectedItem().getLabel()
            self.open_video_list(mode="list", list_id=list_id, filter_label=list_title)
        elif control_id == 6001:
            rating = get_rating_from_user()
            if rating:
                send_rating_for_media_item("movie", self.tmdb_id, rating)
                self.update_states()
        elif control_id == 6002:
            listitems = [ADDON.getLocalizedString(32134), ADDON.getLocalizedString(32135)]
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            account_lists = get_account_lists()
            for item in account_lists:
                listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
            if index == -1:
                pass
            elif index == 0:
                self.open_video_list(mode="favorites")
            elif index == 1:
                self.open_video_list(mode="rating")
            else:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                list_id = account_lists[index - 2]["id"]
                list_title = account_lists[index - 2]["name"]
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                self.open_video_list(mode="list", list_id=list_id, filter_label=list_title, force=True)
        elif control_id == 8:
            self.close()
            xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "movieid": %s }, "options":{ "resume": %s } }, "id": 1 }' % (str(self.data["general"]['dbid']), "false"))
        elif control_id == 9:
            self.close()
            xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "movieid": %s }, "options":{ "resume": %s } }, "id": 1 }' % (str(self.data["general"]['dbid']), "true"))
        elif control_id == 445:
            self.show_manage_dialog()
        elif control_id == 132:
            w = TextViewerDialog('DialogTextViewer.xml', ADDON_PATH, header=xbmc.getLocalizedString(207), text=self.data["general"]["Plot"], color=self.data["general"]['ImageColor'])
            w.doModal()
        elif control_id == 6003:
            if self.data["account_states"]["favorite"]:
                change_fav_status(self.data["general"]["id"], "movie", "false")
            else:
                change_fav_status(self.data["general"]["id"], "movie", "true")
            self.update_states()
        elif control_id == 6006:
            self.open_video_list(mode="rating")
        elif control_id == 6005:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = [ADDON.getLocalizedString(32139)]
            account_lists = get_account_lists()
            for item in account_lists:
                listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            listitems.append(ADDON.getLocalizedString(32138))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
            if index == 0:
                listname = xbmcgui.Dialog().input(ADDON.getLocalizedString(32137), type=xbmcgui.INPUT_ALPHANUM)
                if listname:
                    list_id = create_list(listname)
                    xbmc.sleep(1000)
                    change_list_status(list_id, self.tmdb_id, True)
            elif index == len(listitems) - 1:
                self.remove_list_dialog(account_lists)
            elif index > 0:
                change_list_status(account_lists[index - 1]["id"], self.tmdb_id, True)
                self.update_states()

    def sort_lists(self, lists):
        if not self.logged_in:
            return lists
        account_list = get_account_lists(10)  # use caching here, forceupdate everywhere else
        own_lists = []
        misc_lists = []
        id_list = [item["id"] for item in account_list]
        for item in lists:
            if item["id"] in id_list:
                item["account"] = "True"
                own_lists.append(item)
            else:
                misc_lists.append(item)
        # own_lists = [item for item in lists if item["id"] in id_list]
        # misc_lists = [item for item in lists if item["id"] not in id_list]
        return own_lists + misc_lists

    def update_states(self, forceupdate=True):
        if forceupdate:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            self.update = extended_movie_info(self.tmdb_id, self.dbid, 0)
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

    def remove_list_dialog(self, account_lists):
        listitems = []
        for item in account_lists:
            listitems.append("%s (%i)" % (item["name"], item["item_count"]))
        prettyprint(account_lists)
        index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32138), listitems)
        if index >= 0:
            # change_list_status(account_lists[index]["id"], self.tmdb_id, False)
            remove_list(account_lists[index]["id"])
            self.update_states()

    def show_manage_dialog(self):
        manage_list = []
        listitems = []
        movie_id = str(self.data["general"].get("dbid", ""))
        # filename = self.data["general"].get("FilenameAndPath", False)
        imdb_id = str(self.data["general"].get("imdb_id", ""))
        if movie_id:
            manage_list += [[xbmc.getLocalizedString(413), "RunScript(script.artwork.downloader,mode=gui,mediatype=movie,dbid=" + movie_id + ")"],
                            [xbmc.getLocalizedString(14061), "RunScript(script.artwork.downloader, mediatype=movie, dbid=" + movie_id + ")"],
                            [ADDON.getLocalizedString(32101), "RunScript(script.artwork.downloader,mode=custom,mediatype=movie,dbid=" + movie_id + ",extrathumbs)"],
                            [ADDON.getLocalizedString(32100), "RunScript(script.artwork.downloader,mode=custom,mediatype=movie,dbid=" + movie_id + ")"]]
        else:
            manage_list += [[ADDON.getLocalizedString(32165), "RunPlugin(plugin://plugin.video.couchpotato_manager/movies/add?imdb_id=" + imdb_id + ")||Notification(script.extendedinfo,Added Movie To CouchPota))"]]
        # if xbmc.getCondVisibility("system.hasaddon(script.tvtunes)") and movie_id:
        #     manage_list.append([ADDON.getLocalizedString(32102), "RunScript(script.tvtunes,mode=solo&amp;tvpath=$ESCINFO[Window.Property(movie.FilenameAndPath)]&amp;tvname=$INFO[Window.Property(movie.TVShowTitle)])"])
        if xbmc.getCondVisibility("system.hasaddon(script.libraryeditor)") and movie_id:
            manage_list.append([ADDON.getLocalizedString(32103), "RunScript(script.libraryeditor,DBID=" + movie_id + ")"])
        manage_list.append([xbmc.getLocalizedString(1049), "Addon.OpenSettings(script.extendedinfo)"])
        for item in manage_list:
            listitems.append(item[0])
        selection = xbmcgui.Dialog().select(ADDON.getLocalizedString(32133), listitems)
        if selection > -1:
            for item in manage_list[selection][1].split("||"):
                xbmc.executebuiltin(item)


class JoinOmdbThread(threading.Thread):

    def __init__(self, omdb_thread, window_id):
        threading.Thread.__init__(self)
        self.omdb_thread = omdb_thread
        self.window_id = window_id

    def run(self):
        self.omdb_thread.join()
        if xbmcgui.getCurrentWindowDialogId() == self.window_id:
            pass_dict_to_skin(self.omdb_thread.listitems, "movie.omdb.", False, False, self.window_id)


class SetItemsThread(threading.Thread):

    def __init__(self, set_id=""):
        threading.Thread.__init__(self)
        self.set_id = set_id

    def run(self):
        if self.set_id:
            self.listitems, self.setinfo = get_set_movies(self.set_id)
            self.id_list = [item["id"] for item in self.listitems]
        else:
            self.id_list = []
            self.listitems = []
            self.setinfo = {}
