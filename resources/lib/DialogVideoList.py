# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from TheMovieDB import *
from BaseClasses import *
from WindowManager import wm

SORTS = {"movie": {ADDON.getLocalizedString(32110): "popularity",
                   xbmc.getLocalizedString(172): "release_date",
                   ADDON.getLocalizedString(32108): "revenue",
                   # "Release Date": "primary_release_date",
                   xbmc.getLocalizedString(20376): "original_title",
                   ADDON.getLocalizedString(32112): "vote_average",
                   ADDON.getLocalizedString(32111): "vote_count"},
         "tv": {ADDON.getLocalizedString(32110): "popularity",
                xbmc.getLocalizedString(20416): "first_air_date",
                ADDON.getLocalizedString(32112): "vote_average",
                ADDON.getLocalizedString(32111): "vote_count"},
         "favorites": {ADDON.getLocalizedString(32157): "created_at"},
         "list": {ADDON.getLocalizedString(32157): "created_at"},
         "rating": {ADDON.getLocalizedString(32157): "created_at"}}
TRANSLATIONS = {"movie": xbmc.getLocalizedString(20338),
                "tv": xbmc.getLocalizedString(20364),
                "person": ADDON.getLocalizedString(32156)}

include_adult = str(ADDON.getSetting("include_adults")).lower()


class DialogVideoList(DialogBaseList, WindowXML if ADDON.getSetting("window_mode") == "true" else DialogXML):

    @busy_dialog
    def __init__(self, *args, **kwargs):
        super(DialogVideoList, self).__init__(*args, **kwargs)
        self.type = kwargs.get('type', "movie")
        self.search_str = kwargs.get('search_str', "")
        self.filter_label = kwargs.get("filter_label", "")
        self.mode = kwargs.get("mode", "filter")
        self.list_id = kwargs.get("list_id", False)
        self.sort = kwargs.get('sort', "popularity")
        self.sort_label = kwargs.get('sort_label', ADDON.getLocalizedString(32110))
        self.order = kwargs.get('order', "desc")
        force = kwargs.get('force', False)
        self.logged_in = check_login()
        self.filters = kwargs.get('filters', [])
        if self.listitem_list:
            self.listitems = create_listitems(self.listitem_list)
            self.total_items = len(self.listitem_list)
        else:
            self.update_content(force_update=force)

    def onClick(self, control_id):
        super(DialogVideoList, self).onClick(control_id)
        if control_id in [500]:
            self.last_position = self.getControl(control_id).getSelectedPosition()
            media_id = self.getControl(control_id).getSelectedItem().getProperty("id")
            dbid = self.getControl(control_id).getSelectedItem().getProperty("dbid")
            media_type = self.getControl(control_id).getSelectedItem().getProperty("media_type")
            if media_type:
                self.type = media_type
            if self.type == "tv":
                wm.open_tvshow_info(prev_window=self,
                                    tvshow_id=media_id,
                                    dbid=dbid)
            elif self.type == "person":
                wm.open_actor_info(prev_window=self,
                                   actor_id=media_id)
            else:
                wm.open_movie_info(prev_window=self,
                                   movie_id=media_id,
                                   dbid=dbid)
        elif control_id == 5002:
            self.get_genre()
            self.update()
        elif control_id == 5003:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno(heading=ADDON.getLocalizedString(32151),
                               line1=ADDON.getLocalizedString(32106),
                               nolabel=ADDON.getLocalizedString(32150),
                               yeslabel=ADDON.getLocalizedString(32149))
            result = xbmcgui.Dialog().input(heading=xbmc.getLocalizedString(345),
                                            default="",
                                            type=xbmcgui.INPUT_NUMERIC)
            if result:
                if ret:
                    order = "lte"
                    value = "%s-12-31" % result
                    label = " < " + result
                else:
                    order = "gte"
                    value = "%s-01-01" % result
                    label = " > " + result
                if self.type == "tv":
                    self.add_filter("first_air_date.%s" % order, value, xbmc.getLocalizedString(20416), label)
                else:
                    self.add_filter("primary_release_date.%s" % order, value, xbmc.getLocalizedString(345), label)
                self.mode = "filter"
                self.page = 1
                self.update()
        elif control_id == 5012:
            dialog = xbmcgui.Dialog()
            ret = True
            if not self.type == "tv":
                ret = dialog.yesno(heading=ADDON.getLocalizedString(32151),
                                   line1=ADDON.getLocalizedString(32106),
                                   nolabel=ADDON.getLocalizedString(32150),
                                   yeslabel=ADDON.getLocalizedString(32149))
            result = xbmcgui.Dialog().input(heading=xbmc.getLocalizedString(32111),
                                            default="",
                                            type=xbmcgui.INPUT_NUMERIC)
            if result:
                if ret:
                    order = "lte"
                    label = " < " + result
                else:
                    order = "gte"
                    label = " > " + result
                self.add_filter("vote_count.%s" % order, result, ADDON.getLocalizedString(32111), label)
                self.mode = "filter"
                self.page = 1
                self.update()
        elif control_id == 5004:
            if self.order == "asc":
                self.order = "desc"
            else:
                self.order = "asc"
            self.update()
        elif control_id == 5006:
            self.get_certification()
            self.update()
        elif control_id == 5008:
            self.get_actor()
            self.update()
        elif control_id == 5009:
            self.get_keyword()
            self.update()
        elif control_id == 5010:
            self.get_company()
            self.update()
        elif control_id == 5007:
            self.filters = []
            self.page = 1
            self.mode = "filter"
            if self.type == "tv":
                self.type = "movie"
            else:
                self.type = "tv"
            self.update()
        elif control_id == 7000:
            if self.type == "tv":
                listitems = [ADDON.getLocalizedString(32145)]  # rated tv
                if self.logged_in:
                    listitems.append(ADDON.getLocalizedString(32144))   # starred tv
            else:
                listitems = [ADDON.getLocalizedString(32135)]  # rated movies
                if self.logged_in:
                    listitems.append(ADDON.getLocalizedString(32134))   # starred movies
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            if self.logged_in:
                account_lists = get_account_lists()
                for item in account_lists:
                    listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32136),
                                            list=listitems)
            if index == -1:
                pass
            elif index == 0:
                self.mode = "rating"
                self.sort = "created_at"
                self.sort_label = ADDON.getLocalizedString(32157)
                self.filters = []
                self.page = 1
                self.update()
            elif index == 1:
                self.mode = "favorites"
                self.sort = "created_at"
                self.sort_label = ADDON.getLocalizedString(32157)
                self.filters = []
                self.page = 1
                self.update()
            else:
                # offset = len(listitems) - len(account_lists)
                # notify(str(offset))
                list_id = account_lists[index - 2]["id"]
                list_title = account_lists[index - 2]["name"]
                self.close()
                dialog = DialogVideoList(u'script-%s-VideoList.xml' % ADDON_NAME, ADDON_PATH,
                                         color=self.color,
                                         filters=[],
                                         mode="list",
                                         list_id=list_id,
                                         filter_label=list_title)
                dialog.doModal()

    def update_ui(self):
        super(DialogVideoList, self).update_ui()
        self.window.setProperty("Type", TRANSLATIONS[self.type])
        if self.type == "tv":
            self.window.getControl(5006).setVisible(False)
            self.window.getControl(5008).setVisible(False)
            self.window.getControl(5009).setVisible(False)
            self.window.getControl(5010).setVisible(False)
        else:
            self.window.getControl(5006).setVisible(True)
            self.window.getControl(5008).setVisible(True)
            self.window.getControl(5009).setVisible(True)
            self.window.getControl(5010).setVisible(True)

    def go_to_next_page(self):
        if self.page < self.total_pages:
            self.page += 1

    def go_to_prev_page(self):
        if self.page > 1:
            self.page -= 1

    def context_menu(self):
        focus_id = self.getFocusId()
        if not focus_id == 500:
            return None
        item_id = self.getControl(focus_id).getSelectedItem().getProperty("id")
        if self.type == "tv":
            listitems = [ADDON.getLocalizedString(32169)]
        else:
            listitems = [ADDON.getLocalizedString(32113)]
        if self.logged_in:
            listitems += [xbmc.getLocalizedString(14076)]
            if not self.type == "tv":
                listitems += [ADDON.getLocalizedString(32107)]
            if self.mode == "list":
                listitems += [ADDON.getLocalizedString(32035)]
        # context_menu = ContextMenu.ContextMenu(u'DialogContextMenu.xml', ADDON_PATH, labels=listitems)
        # context_menu.doModal()
        selection = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32151),
                                            list=listitems)
        if selection == 0:
            rating = get_rating_from_user()
            if rating:
                send_rating_for_media_item(media_type=self.type,
                                           media_id=item_id,
                                           rating=rating)
                xbmc.sleep(2000)
                self.update(force_update=True)
        elif selection == 1:
            change_fav_status(media_id=item_id,
                              media_type=self.type,
                              status="true")
        elif selection == 2:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = [ADDON.getLocalizedString(32139)]
            account_lists = get_account_lists()
            for item in account_lists:
                listitems.append("%s (%i)" % (item["name"], item["item_count"]))
            listitems.append(ADDON.getLocalizedString(32138))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            index = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32136),
                                            list=listitems)
            if index == 0:
                listname = xbmcgui.Dialog().input(heading=ADDON.getLocalizedString(32137),
                                                  type=xbmcgui.INPUT_ALPHANUM)
                if listname:
                    list_id = create_list(listname)
                    xbmc.sleep(1000)
                    change_list_status(list_id=list_id,
                                       movie_id=item_id,
                                       status=True)
            elif index == len(listitems) - 1:
                self.remove_list_dialog(account_lists)
            elif index > 0:
                change_list_status(account_lists[index - 1]["id"], item_id, True)
                # xbmc.sleep(2000)
                # self.update(force_update=True)
        elif selection == 3:
            change_list_status(self.list_id, item_id, False)
            self.update(force_update=True)

    def get_sort_type(self):
        listitems = []
        sort_strings = []
        if self.mode in ["favorites", "rating", "list"]:
            sort_key = self.mode
        else:
            sort_key = self.type
        for (key, value) in SORTS[sort_key].iteritems():
            listitems.append(key)
            sort_strings.append(value)
        index = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32104),
                                        list=listitems)
        if index > -1:
            if sort_strings[index] == "vote_average":
                self.add_filter(key="vote_count.gte",
                                value="10",
                                typelabel="%s (%s)" % (ADDON.getLocalizedString(32111), xbmc.getLocalizedString(21406)),
                                label="10")
            self.sort = sort_strings[index]
            self.sort_label = listitems[index]

    def add_filter(self, key, value, typelabel, label):
        if ".gte" in key or ".lte" in key:
            super(DialogVideoList, self).add_filter(key=key,
                                                    value=value,
                                                    typelabel=typelabel,
                                                    label=label,
                                                    force_overwrite=True)
        else:
            super(DialogVideoList, self).add_filter(key=key,
                                                    value=value,
                                                    typelabel=typelabel,
                                                    label=label,
                                                    force_overwrite=False)

    def get_genre(self):
        response = get_tmdb_data("genre/%s/list?language=%s&" % (self.type, ADDON.getSetting("LanguageID")), 10)
        id_list = [item["id"] for item in response["genres"]]
        label_list = [item["name"] for item in response["genres"]]
        index = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32151),
                                        list=label_list)
        if index > -1:
            self.add_filter("with_genres", str(id_list[index]), xbmc.getLocalizedString(135), str(label_list[index]))
            self.mode = "filter"
            self.page = 1

    def get_actor(self):
        result = xbmcgui.Dialog().input(heading=xbmc.getLocalizedString(16017),
                                        default="",
                                        type=xbmcgui.INPUT_ALPHANUM)
        if result and result > -1:
            response = get_person_info(result)
            if result == -1:
                return None
            self.add_filter("with_people", str(response["id"]), ADDON.getLocalizedString(32156), response["name"])
            self.mode = "filter"
            self.page = 1

    def get_company(self):
        result = xbmcgui.Dialog().input(heading=xbmc.getLocalizedString(16017),
                                        default="",
                                        type=xbmcgui.INPUT_ALPHANUM)
        if result and result > -1:
            response = search_company(result)
            if result == -1:
                return None
            if len(response) > 1:
                names = [item["name"] for item in response]
                selection = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32151),
                                                    list=names)
                if selection > -1:
                    response = response[selection]
            elif response:
                response = response[0]
            else:
                notify("no company found")
            self.add_filter(key="with_companies",
                            value=str(response["id"]),
                            typelabel=xbmc.getLocalizedString(20388),
                            label=response["name"])
            self.mode = "filter"
            self.page = 1

    def get_keyword(self):
        result = xbmcgui.Dialog().input(heading=xbmc.getLocalizedString(16017),
                                        default="",
                                        type=xbmcgui.INPUT_ALPHANUM)
        if result and result > -1:
            response = get_keyword_id(result)
            if not response:
                return None
            keyword_id = response["id"]
            name = response["name"]
            if result > -1:
                self.add_filter("with_keywords", str(keyword_id), ADDON.getLocalizedString(32114), name)
                self.mode = "filter"
                self.page = 1

    def get_certification(self):
        response = get_certification_list(self.type)
        country_list = []
        for (key, value) in response.iteritems():
            country_list.append(key)
        index = xbmcgui.Dialog().select(heading=xbmc.getLocalizedString(21879),
                                        list=country_list)
        if index == -1:
            return None
        cert_list = []
        country = country_list[index]
        for item in response[country]:
            label = "%s  -  %s" % (item["certification"], item["meaning"])
            cert_list.append(label)
        index = xbmcgui.Dialog().select(heading=ADDON.getLocalizedString(32151),
                                        list=cert_list)
        if index == -1:
            return None
        cert = cert_list[index].split("  -  ")[0]
        self.add_filter("certification_country", country, ADDON.getLocalizedString(32153), country)
        self.add_filter("certification", cert, ADDON.getLocalizedString(32127), cert)
        self.page = 1
        self.mode = "filter"

    def fetch_data(self, force=False):  # TODO: rewrite
        sort_by = self.sort + "." + self.order
        if self.type == "tv":
            temp = "tv"
            rated = ADDON.getLocalizedString(32145)
            starred = ADDON.getLocalizedString(32144)
        else:
            temp = "movies"
            rated = ADDON.getLocalizedString(32135)
            starred = ADDON.getLocalizedString(32134)
        if self.mode == "search":
            url = "search/multi?query=%s&page=%i&include_adult=%s&" % (urllib.quote_plus(self.search_str), self.page, include_adult)
            if self.search_str:
                self.filter_label = ADDON.getLocalizedString(32146) % self.search_str
            else:
                self.filter_label = ""
        elif self.mode == "list":
            url = "list/%s?language=%s&" % (str(self.list_id), ADDON.getSetting("LanguageID"))
            # self.filter_label = ADDON.getLocalizedString(32036)
        elif self.mode == "favorites":
            url = "account/%s/favorite/%s?language=%s&page=%i&session_id=%s&sort_by=%s&" % (get_account_info(), temp, ADDON.getSetting("LanguageID"), self.page, get_session_id(), sort_by)
            self.filter_label = starred
        elif self.mode == "rating":
            force = True  # workaround, should be updated after setting rating
            if self.logged_in:
                session_id = get_session_id()
                if not session_id:
                    notify("Could not get session id")
                    return {"listitems": [],
                            "results_per_page": 0,
                            "total_results": 0}
                url = "account/%s/rated/%s?language=%s&page=%i&session_id=%s&sort_by=%s&" % (get_account_info(), temp, ADDON.getSetting("LanguageID"), self.page, session_id, sort_by)
            else:
                session_id = get_guest_session_id()
                if not session_id:
                    notify("Could not get session id")
                    return {"listitems": [],
                            "results_per_page": 0,
                            "total_results": 0}
                url = "guest_session/%s/rated_movies?language=%s&" % (session_id, ADDON.getSetting("LanguageID"))
            self.filter_label = rated
        else:
            self.set_filter_url()
            self.set_filter_label()
            url = "discover/%s?sort_by=%s&%slanguage=%s&page=%i&include_adult=%s&" % (self.type, sort_by, self.filter_url, ADDON.getSetting("LanguageID"), self.page, include_adult)
        if force:
            response = get_tmdb_data(url=url,
                                     cache_days=0)
        else:
            response = get_tmdb_data(url=url,
                                     cache_days=2)
        if self.mode == "list":
            info = {"listitems": handle_tmdb_movies(response["items"]),
                    "results_per_page": 1,
                    "total_results": len(response["items"])}
            return info
        if "results" not in response:
            # self.close()
            return {"listitems": [],
                    "results_per_page": 0,
                    "total_results": 0}
        if not response["results"]:
            notify(xbmc.getLocalizedString(284))
        if self.mode == "search":
            listitems = handle_tmdb_multi_search(response["results"])
        elif self.type == "movie":
            listitems = handle_tmdb_movies(results=response["results"],
                                           local_first=False,
                                           sortkey=None)
        else:
            listitems = handle_tmdb_tvshows(results=response["results"],
                                            local_first=False,
                                            sortkey=None)
        info = {"listitems": listitems,
                "results_per_page": response["total_pages"],
                "total_results": response["total_results"]}
        return info
