import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
import DialogVideoInfo
import DialogTVShowInfo
import DialogActorInfo
import ContextMenu
homewindow = xbmcgui.Window(10000)
from TheMovieDB import *

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_strings = addon.getLocalizedString
addon_path = addon.getAddonInfo('path').decode("utf-8")
sorts = {"movie": {"Popularity": "popularity",
                   "Release Date": "release_date",
                   "Revenue": "revenue",
                   "Release Date": "primary_release_date",
                   "Original Title": "original_title",
                   "Vote average": "vote_average",
                   "Vote Count": "vote_count"},
            "tv": {"Popularity": "popularity",
                   "First Air Date": "first_air_date",
                   "Vote average": "vote_average",
                   "Vote Count": "vote_count"},
     "favourite": {"Created at": "created_at"}}


class DialogVideoList(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.listitem_list = kwargs.get('listitems', None)
        self.color = kwargs.get('color', "FFAAAAAA")
        self.type = kwargs.get('type', "movie")
        self.search_string = kwargs.get('search_string', "")
        self.page = 1
        self.totalpages = 1
        self.mode = kwargs.get("mode", "filter")
        self.sort = kwargs.get('sort', "popularity")
        self.sort_label = kwargs.get('sort', "Popularity")
        self.order = kwargs.get('order', "desc")
        self.filters = kwargs.get('filters', [])
        if self.listitem_list:
            self.listitems = CreateListItems(self.listitem_list)
        else:
            self.update_content()
            # Notify(str(self.totalpages))
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        homewindow.setProperty("WindowColor", self.color)
        self.windowid = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.windowid)
        self.window.setProperty("WindowColor", self.color)
        self.update_list()
        xbmc.sleep(200)
        xbmc.executebuiltin("SetFocus(500)")

    def onAction(self, action):
        focusid = self.getFocusId()
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            if focusid == 500:
                list_id = self.getControl(focusid).getSelectedItem().getProperty("id")
                listitems = ["Add To Favourites", "Rate Movie", "Add to List"]
                # context_menu = ContextMenu.ContextMenu(u'script-globalsearch-contextmenu.xml', addon_path, labels=listitems)
                # context_menu.doModal()
                selection = xbmcgui.Dialog().select("Choose Option", listitems)
                if selection == 0:
                    ChangeFavStatus(list_id, self.type, "true")
                elif selection == 1:
                    ratings = []
                    for i in range(0, 21):
                        ratings.append(str(float(i * 0.5)))
                    rating = xbmcgui.Dialog().select("Enter Rating", ratings)
                    if rating > -1:
                        rating = float(rating) * 0.5
                        RateMedia(self.type, list_id, rating)
                elif selection == 2:
                    pass

        # if xbmc.getCondVisibility("Container(500).Row(1)"):
        #     self.page += 1
        #     self.update_content(add=True)

    def onClick(self, controlID):
        if controlID in [500]:
            AddToWindowStack(self)
            self.close()
            media_id = self.getControl(controlID).getSelectedItem().getProperty("id")
            media_type = self.getControl(controlID).getSelectedItem().getProperty("media_type")
            if media_type:
                self.type = media_type
            if self.type == "tv":
                dialog = DialogTVShowInfo.DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=media_id)
            elif self.type == "person":
                dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % addon_name, addon_path, id=media_id)
            else:
                dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=media_id)
            dialog.doModal()
        elif controlID == 5001:
            self.get_sort_type()
            self.update_content()
            self.update_list()
        elif controlID == 5002:
            self.get_genre()
            self.update_content()
            self.update_list()
        elif controlID == 5003:
            result = xbmcgui.Dialog().input("Enter Year", "", type=xbmcgui.INPUT_NUMERIC)
            if self.type == "tv":
                self.add_filter("first_air_date_year", str(result), "First Air Date", str(result))
            else:
                self.add_filter("year", str(result), "Year", str(result))
            self.mode = "filter"
            self.page = 1
            self.update_content()
            self.update_list()
        elif controlID == 5004:
            if self.order == "asc":
                self.order = "desc"
            else:
                self.order = "asc"
            self.update_content()
            self.update_list()
        elif controlID == 5005:
            self.filters = []
            self.page = 1
            self.mode = "filter"
            self.update_content()
            self.update_list()
        elif controlID == 5006:
            self.get_certification()
            self.update_content()
            self.update_list()
        elif controlID == 5008:
            self.get_actor()
            self.update_content()
            self.update_list()
        elif controlID == 5009:
            self.get_keyword()
            self.update_content()
            self.update_list()
        elif controlID == 5007:
            self.filters = []
            self.page = 1
            self.mode = "filter"
            if self.type == "tv":
                self.type = "movie"
            else:
                self.type = "tv"
            self.update_content()
            self.update_list()
        elif controlID == 6000:
            result = xbmcgui.Dialog().input("Enter Search String", "", type=xbmcgui.INPUT_ALPHANUM)
            if result and result > -1:
                self.search_string = result
                self.filters = []
                self.mode = "search"
                self.page = 1
                self.update_content()
                self.update_list()
        elif controlID == 7000:
            listitems = ["Starred Movies", "Rated Movies"]
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            account_lists = GetAccountLists()
            for item in account_lists:
                listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select("Choose List", listitems)
            if index == -1:
                pass
            elif index == 0:
                pass
            elif index == 1:
                pass
            else:
                pass

    def onFocus(self, controlID):
        if controlID == 600:
            if self.page < self.totalpages:
                self.page += 1
                self.update_content()
                self.update_list()
        if controlID == 700:
            if self.page > 1:
                self.page -= 1
                self.update_content()
                self.update_list()


    def get_sort_type(self):
        listitems = []
        sort_strings = []
        for (key, value) in sorts[self.type].iteritems():
            listitems.append(key)
            sort_strings.append(value)
        index = xbmcgui.Dialog().select("Choose Sort Order", listitems)
        if index > -1:
            if sort_strings[index] == "vote_average":
                self.add_filter("vote_count.gte", "10", "Vote Count (greater)", "10")
            self.sort = sort_strings[index]
            self.sort_label = listitems[index]

    def add_filter(self, key, value, typelabel, label):
        index = False
        new_filter = {"id": value,
                       "type": key,
                       "typelabel": typelabel,
                       "label": label}
        if new_filter in self.filters:
            return False
        for i, item in enumerate(self.filters):
            if item["type"] == key:
                index = i
                break
        if index:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno(heading="Choose Mode", line1="Choose the filter behaviour", nolabel="OR", yeslabel="AND")
            if ret:
                self.filters[index]["id"] = self.filters[index]["id"] + "," + str(value)
                self.filters[index]["label"] = self.filters[index]["label"] + "," + str(label)
            else:
                self.filters[index]["id"] = self.filters[index]["id"] + "|" + str(value)
                self.filters[index]["label"] = self.filters[index]["label"] + "|" + str(label)
        else:
            self.filters.append(new_filter)


    def set_filter_url(self):
        filter_list = []
        prettyprint(self.filters)
        for item in self.filters:
            filter_list.append("%s=%s" % (item["type"], urllib.quote_plus(item["id"])))
        self.filter_url = "&".join(filter_list)

    def set_filter_label(self):
        filter_list = []
        prettyprint(self.filters)
        for item in self.filters:
            filter_list.append("%s: %s" % (item["typelabel"], item["label"].replace("|", " | ").replace(",", " + ")))
        self.filter_label = "  -  ".join(filter_list)


    def get_genre(self):
        response = GetMovieDBData("genre/%s/list?language=%s&" % (self.type, addon.getSetting("LanguageID")), 10)
        id_list = []
        label_list = []
        for item in response["genres"]:
            id_list.append(item["id"])
            label_list.append(item["name"])
        index = xbmcgui.Dialog().select("Choose Genre", label_list)
        if index > -1:
            # return "with_genres=" + str(id_list[index])
            self.add_filter("with_genres", str(id_list[index]), "Genres", str(label_list[index]))
            self.mode = "filter"
            self.page = 1

    def get_actor(self):
        result = xbmcgui.Dialog().input("Enter Search String", "", type=xbmcgui.INPUT_ALPHANUM)
        if result and result > -1:
            response = GetPersonID(result)
            prettyprint(response)
            if result > -1:
                # return "with_genres=" + str(id_list[index])
                self.add_filter("with_people", str(response), "People", "Personname (to-do)")
                self.mode = "filter"
                self.page = 1

    def get_keyword(self):
        result = xbmcgui.Dialog().input("Enter Search String", "", type=xbmcgui.INPUT_ALPHANUM)
        if result and result > -1:
            response = GetKeywordID(result)
            prettyprint(response)
            if result > -1:
                # return "with_genres=" + str(id_list[index])
                self.add_filter("with_keywords", str(response), "Keywords", "Keyword Label (to-do)")
                self.mode = "filter"
                self.page = 1

    def get_certification(self):
        response = get_certification_list(self.type)
        country_list = []
        for (key, value) in response.iteritems():
            country_list.append(key)
        index = xbmcgui.Dialog().select("Choose Country", country_list)
        if index > -1:
            cert_list = []
            # for (key, value) in response[country_list[index]].iteritems():
            #     cert_list.append(key)
            country = country_list[index]
            for item in response[country]:
                label = "%s  -  %s" % (item["certification"], item["meaning"])
                cert_list.append(label)
            index = xbmcgui.Dialog().select("Choose Certification", cert_list)
            if index > -1:
            # return "with_genres=" + str(id_list[index])
                cert = cert_list[index].split("  -  ")[0]
                self.add_filter("certification_country", country, "Certification Country", country)
                self.add_filter("certification", cert, "Certification", cert)
                self.page = 1
                self.mode = "filter"

    def update_content(self, add=False):
        if add:
            self.old_items = self.listitems
        else:
            self.old_items = []
        self.listitems, self.totalpages = self.fetch_data()
        self.listitems_2 = []
        # if self.page < self.totalpages:
        #     self.page += 1
        #     self.listitems_2, self.totalpages = self.fetch_data()
        self.listitems = self.old_items + CreateListItems(self.listitems) + CreateListItems(self.listitems_2)
        # for item in (self.page - 1) * 2:
        #     xbmc.executebuiltin("Down")

    def update_list(self):
        self.getControl(500).reset()
        self.getControl(500).addItems(self.listitems)
        self.window.setProperty("TotalPages", str(self.totalpages))
        self.window.setProperty("CurrentPage", str(self.page))
        self.window.setProperty("Type", self.type)
        self.window.setProperty("Filter_Label", self.filter_label)
        self.window.setProperty("Sort_Label", self.sort_label)
        if self.order == "asc":
            self.window.setProperty("Order_Label", "Ascending")
        else:
            self.window.setProperty("Order_Label", "Descending")

    def fetch_data(self):
        temp= "movies"
        temp2 = "movies"
        if self.type == "tv":
            temp = "tv"
            temp2 = "TV Shows"
        if self.mode == "search":
            url = "search/multi?query=%s&page=%i&include_adult=%s&" % (urllib.quote_plus(self.search_string), self.page, addon.getSetting("include_adults"))
            self.filter_label = "Search for '%s'" % self.search_string
        elif self.mode == "favorites":
            url = "account/%s/favorite/%s?language=%s&page=%i&session_id=%s&" % (get_account_info(), temp, addon.getSetting("LanguageID"), self.page, get_session_id())
            self.filter_label = "Starred " + temp2
        elif self.mode == "rating":
            if addon.getSetting("tmdb_username"):
                session_id_string = "session_id=" + get_session_id()
            else:
                session_id_string = "guest_session_id=" + get_guest_session_id()
            url = "account/%s/rated/movies?language=%s&page=%i&%s&" % (get_account_info(), addon.getSetting("LanguageID"), self.page, session_id_string)
            self.filter_label = "Rated " + temp2
        else:
            self.set_filter_url()
            self.set_filter_label()
            sortby = self.sort + "." + self.order
            url = "discover/%s?sort_by=%s&%s&language=%s&page=%i&include_adult=%s&" % (self.type, sortby, self.filter_url, addon.getSetting("LanguageID"), self.page, addon.getSetting("include_adults"))
        response = GetMovieDBData(url, 10)
        if not response["results"]:
            Notify("No results found")
        if self.mode == "search":
            return HandleTMDBMultiSearchResult(response["results"]), response["total_pages"]
        elif self.type == "movie":
            return HandleTMDBMovieResult(response["results"], False, None), response["total_pages"]
        else:
            return HandleTMDBTVShowResult(response["results"], False, None), response["total_pages"]



