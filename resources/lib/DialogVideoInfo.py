import xbmc
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
from omdb import *
import DialogActorInfo
import DialogVideoList
from ImageTools import *
import threading
from BaseClasses import DialogBaseInfo


class DialogVideoInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogVideoInfo, self).__init__(*args, **kwargs)
        if not ADDON.getSetting("first_start_infodialog"):
            ADDON.setSetting("first_start_infodialog", "True")
            xbmcgui.Dialog().ok(ADDON_NAME, ADDON.getLocalizedString(32140), ADDON.getLocalizedString(32141))
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.monitor = SettingsMonitor()
        tmdb_id = kwargs.get('id')
        self.dbid = kwargs.get('dbid')
        imdb_id = kwargs.get('imdb_id')
        self.name = kwargs.get('name')
        if tmdb_id:
            self.tmdb_id = tmdb_id
        else:
            self.tmdb_id = get_movie_tmdb_id(imdb_id=imdb_id, dbid=self.dbid, name=self.name)
        if self.tmdb_id:
            self.data = GetExtendedMovieInfo(self.tmdb_id, self.dbid)
            if "general" not in self.data:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                return None
            log("Blur image %s with radius %i" % (self.data["general"]["Thumb"], 25))
            youtube_thread = Get_Youtube_Vids_Thread(self.data["general"]["Label"] + " " + self.data["general"]["Year"] + ", movie", "", "relevance", 15)
            sets_thread = Get_Set_Items_Thread(self.data["general"]["SetId"])
            self.omdb_thread = Threaded_Function(GetOmdbMovieInfo, self.data["general"]["imdb_id"])
            lists_thread = Threaded_Function(self.SortLists, self.data["lists"])
            self.omdb_thread.start()
            sets_thread.start()
            youtube_thread.start()
            lists_thread.start()
            if "DBID" not in self.data["general"]:
                poster_thread = Threaded_Function(Get_File, self.data["general"]["Poster"])
                poster_thread.start()
            vid_id_list = [item["key"] for item in self.data["videos"]]
            self.crew_list = []
            crew_id_list = []
            for item in self.data["crew"]:
                if item["id"] not in crew_id_list:
                    crew_id_list.append(item["id"])
                    self.crew_list.append(item)
                else:
                    index = crew_id_list.index(item["id"])
                    self.crew_list[index]["job"] = self.crew_list[index]["job"] + " / " + item["job"]
            if "DBID" not in self.data["general"]:
                poster_thread.join()
                self.data["general"]['Poster'] = poster_thread.listitems
            filter_thread = Filter_Image_Thread(self.data["general"]["Thumb"], 25)
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
            self.data["similar"] = [item for item in self.data["similar"] if item["ID"] not in id_list]
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
                              (750, create_listitems(self.crew_list, 0)),
                              (850, create_listitems(self.data["genres"], 0)),
                              (950, create_listitems(self.data["keywords"], 0)),
                              (1050, create_listitems(self.data["reviews"], 0)),
                              (1150, create_listitems(self.data["videos"], 0)),
                              (1250, create_listitems(self.data["images"], 0)),
                              (1350, create_listitems(self.data["backdrops"], 0)),
                              (350, create_listitems(youtube_vids, 0))]
        else:
            Notify(ADDON.getLocalizedString(32143))
            self.close()
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        super(DialogVideoInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        self.window.setProperty("type", "movie")
        passDictToSkin(self.data["general"], "movie.", False, False, self.windowid)
        self.fill_lists()
        passDictToSkin(self.setinfo, "movie.set.", False, False, self.windowid)
        self.UpdateStates(False)
        self.join_omdb = Join_Omdb_Thread(self.omdb_thread, self.windowid)
        self.join_omdb.start()

    def onClick(self, controlID):
        control = self.getControl(controlID)
        if controlID in [1000, 750]:
            actorid = control.getSelectedItem().getProperty("id")
            AddToWindowStack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actorid)
            dialog.doModal()
        elif controlID in [150, 250]:
            movieid = control.getSelectedItem().getProperty("id")
            AddToWindowStack(self)
            self.close()
            dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=movieid)
            dialog.doModal()
        elif controlID in [1250, 1350]:
            image = control.getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif controlID in [350, 1150, 10]:
            AddToWindowStack(self)
            self.close()
            listitem = xbmcgui.ListItem(xbmc.getLocalizedString(20410))
            listitem.setInfo('video', {'Title': xbmc.getLocalizedString(20410), 'Genre': 'Youtube Video'})
            if controlID == 10:
                youtube_id = self.getControl(1150).getListItem(0).getProperty("youtube_id")
            else:
                youtube_id = control.getSelectedItem().getProperty("youtube_id")
            if youtube_id:
                self.movieplayer.playYoutubeVideo(youtube_id, control.getSelectedItem(), True)
                self.movieplayer.wait_for_video_end()
                PopWindowStack()
            else:
                Notify(ADDON.getLocalizedString(32052))
        # elif controlID in [8]:
        #     AddToWindowStack(self)
        #     self.close()
        #     listitem = create_listitems([self.data["general"]])[0]
        #     self.movieplayer.play(item=self.data["general"]['FilenameAndPath'], listitem=listitem)
        #     self.movieplayer.wait_for_video_end()
        elif controlID == 550:
            company_id = control.getSelectedItem().getProperty("id")
            company_name = control.getSelectedItem().getLabel()
            filters = [{"id": company_id,
                        "type": "with_companies",
                        "typelabel": xbmc.getLocalizedString(20388),
                        "label": company_name}]
            self.OpenVideoList(filters=filters)
        elif controlID == 1050:
            author = control.getSelectedItem().getProperty("author")
            text = "[B]" + author + "[/B][CR]" + cleanText(control.getSelectedItem().getProperty("content"))
            w = TextViewer_Dialog('DialogTextViewer.xml', ADDON_PATH, header=xbmc.getLocalizedString(185), text=text, color=self.data["general"]['ImageColor'])
            w.doModal()
        elif controlID == 950:
            keyword_id = control.getSelectedItem().getProperty("id")
            keyword_name = control.getSelectedItem().getLabel()
            filters = [{"id": keyword_id,
                        "type": "with_keywords",
                        "typelabel": ADDON.getLocalizedString(32114),
                        "label": keyword_name}]
            self.OpenVideoList(filters=filters)
        elif controlID == 850:
            genre_id = control.getSelectedItem().getProperty("id")
            genre_name = control.getSelectedItem().getLabel()
            filters = [{"id": genre_id,
                        "type": "with_genres",
                        "typelabel": xbmc.getLocalizedString(135),
                        "label": genre_name}]
            self.OpenVideoList(filters=filters)
        elif controlID == 650:
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
            self.OpenVideoList(filters=filters)
        elif controlID == 450:
            list_id = control.getSelectedItem().getProperty("id")
            list_title = control.getSelectedItem().getLabel()
            self.OpenVideoList(mode="list", list_id=list_id, filter_label=list_title)
        elif controlID == 6001:
            rating = get_rating_from_user()
            if rating:
                send_rating_for_media_item("movie", self.tmdb_id, rating)
                self.UpdateStates()
        elif controlID == 6002:
            listitems = [ADDON.getLocalizedString(32134), ADDON.getLocalizedString(32135)]
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            account_lists = GetAccountLists()
            for item in account_lists:
                listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
            if index == -1:
                pass
            elif index == 0:
                self.OpenVideoList(mode="favorites")
            elif index == 1:
                self.OpenVideoList(mode="rating")
            else:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                list_id = account_lists[index - 2]["id"]
                list_title = account_lists[index - 2]["name"]
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                self.OpenVideoList(mode="list", list_id=list_id, filter_label=list_title, force=True)
        elif controlID == 8:
            self.close()
            xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "movieid": %i }, "options":{ "resume": %s } }, "id": 1 }' % (self.data["general"]['DBID'], "false"))
        elif controlID == 9:
            self.close()
            xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "movieid": %i }, "options":{ "resume": %s } }, "id": 1 }' % (self.data["general"]['DBID'], "true"))
        elif controlID == 445:
            self.ShowManageDialog()
        elif controlID == 132:
            w = TextViewer_Dialog('DialogTextViewer.xml', ADDON_PATH, header=xbmc.getLocalizedString(207), text=self.data["general"]["Plot"], color=self.data["general"]['ImageColor'])
            w.doModal()
        elif controlID == 6003:
            if self.data["account_states"]["favorite"]:
                ChangeFavStatus(self.data["general"]["ID"], "movie", "false")
            else:
                ChangeFavStatus(self.data["general"]["ID"], "movie", "true")
            self.UpdateStates()
        elif controlID == 6006:
            self.ShowRatedMovies()
        elif controlID == 6005:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = [ADDON.getLocalizedString(32139)]
            account_lists = GetAccountLists()
            for item in account_lists:
                listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            listitems.append(ADDON.getLocalizedString(32138))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
            if index == 0:
                listname = xbmcgui.Dialog().input(ADDON.getLocalizedString(32137), type=xbmcgui.INPUT_ALPHANUM)
                if listname:
                    list_id = CreateList(listname)
                    xbmc.sleep(1000)
                    ChangeListStatus(list_id, self.tmdb_id, True)
            elif index == len(listitems) - 1:
                self.RemoveListDialog(account_lists)
            elif index > 0:
                ChangeListStatus(account_lists[index - 1]["id"], self.tmdb_id, True)
                self.UpdateStates()

    def SortLists(self, lists):
        if not self.logged_in:
            return lists
        account_list = GetAccountLists(10)  # use caching here, forceupdate everywhere else
        own_lists = []
        misc_lists = []
        id_list = [item["id"] for item in account_list]
        for item in lists:
            if item["ID"] in id_list:
                item["account"] = "True"
                own_lists.append(item)
            else:
                misc_lists.append(item)
        # own_lists = [item for item in lists if item["ID"] in id_list]
        # misc_lists = [item for item in lists if item["ID"] not in id_list]
        return own_lists + misc_lists

    def UpdateStates(self, forceupdate=True):
        if forceupdate:
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            self.update = GetExtendedMovieInfo(self.tmdb_id, self.dbid, 0)
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
            # Notify(str(self.data["account_states"]["rated"]["value"]))

    def RemoveListDialog(self, account_lists):
        listitems = []
        for item in account_lists:
            listitems.append("%s (%i)" % (item["name"], item["item_count"]))
        prettyprint(account_lists)
        index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32138), listitems)
        if index >= 0:
            # ChangeListStatus(account_lists[index]["id"], self.tmdb_id, False)
            RemoveList(account_lists[index]["id"])
            self.UpdateStates()

    def ShowRatedMovies(self):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        listitems = GetRatedMedia("movies")
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        self.OpenVideoList(listitems=listitems)

    def ShowManageDialog(self):
        manage_list = []
        listitems = []
        movie_id = str(self.data["general"].get("DBID", ""))
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


class Join_Omdb_Thread(threading.Thread):

    def __init__(self, omdb_thread, windowid):
        threading.Thread.__init__(self)
        self.omdb_thread = omdb_thread
        self.windowid = windowid

    def run(self):
        self.omdb_thread.join()
        if xbmcgui.getCurrentWindowDialogId() == self.windowid:
            passDictToSkin(self.omdb_thread.listitems, "movie.omdb.", False, False, self.windowid)


class Get_Set_Items_Thread(threading.Thread):

    def __init__(self, set_id=""):
        threading.Thread.__init__(self)
        self.set_id = set_id

    def run(self):
        if self.set_id:
            self.listitems, self.setinfo = GetSetMovies(self.set_id)
            self.id_list = [item["ID"] for item in self.listitems]
        else:
            self.id_list = []
            self.listitems = []
            self.setinfo = {}


class SettingsMonitor(xbmc.Monitor):

    def __init__(self):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        xbmc.sleep(300)
