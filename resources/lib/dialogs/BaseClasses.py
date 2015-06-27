# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from ..Utils import *
from ..TheMovieDB import *
from ..WindowManager import wm
from T9Search import T9Search
from collections import deque
import ast
from ..OnClickHandler import OnClickHandler
from .. import VideoPlayer

PLAYER = VideoPlayer.VideoPlayer()
ch = OnClickHandler()


class WindowXML(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self)
        self.window_type = "window"

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowId()
        self.window = xbmcgui.Window(self.window_id)


class DialogXML(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.window_type = "dialog"

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.window_id)


class DialogBaseList(object):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        super(DialogBaseList, self).__init__(*args, **kwargs)
        self.listitem_list = kwargs.get('listitems', None)
        self.last_searches = deque(maxlen=10)
        self.color = kwargs.get('color', "FFAAAAAA")
        self.page = 1
        self.column = None
        self.last_position = 0
        self.total_pages = 1
        self.total_items = 0
        check_version()

    def onInit(self):
        super(DialogBaseList, self).onInit()
        HOME.setProperty("WindowColor", self.color)
        self.window.setProperty("WindowColor", self.color)
        self.update_ui()
        xbmc.sleep(200)
        if self.total_items > 0:
            xbmc.executebuiltin("SetFocus(500)")
            self.getControl(500).selectItem(self.last_position)
        else:
            xbmc.executebuiltin("SetFocus(6000)")

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            wm.pop_stack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            self.context_menu()

    def onFocus(self, control_id):
        old_page = self.page
        if control_id == 600:
            self.go_to_next_page()
        elif control_id == 700:
            self.go_to_prev_page()
        if self.page != old_page:
            self.update()

    def onClick(self, control_id):
        if control_id == 5001:
            self.get_sort_type()
            self.update()
        elif control_id == 5005:
            self.filters = []
            self.page = 1
            self.mode = "filter"
            self.update()
        elif control_id == 6000:
            settings_str = SETTING("search_history")
            if settings_str:
                self.last_searches = deque(ast.literal_eval(settings_str), maxlen=10)
            dialog = T9Search(u'script-%s-T9Search.xml' % ADDON_NAME, ADDON_PATH,
                              call=self.search,
                              start_value=self.search_str,
                              history=self.last_searches)
            dialog.doModal()
            if dialog.classic_mode:
                result = xbmcgui.Dialog().input(heading=LANG(16017),
                                                type=xbmcgui.INPUT_ALPHANUM)
                if result and result > -1:
                    self.search(result)
            if self.search_str:
                listitem = {"label": self.search_str}
                if listitem in self.last_searches:
                    self.last_searches.remove(listitem)
                self.last_searches.appendleft(listitem)
                setting_str = str(list(self.last_searches))
                ADDON.setSetting("search_history", setting_str)
            if self.total_items > 0:
                self.setFocusId(500)

    def search(self, label):
        self.search_str = label
        self.mode = "search"
        self.filters = []
        self.page = 1
        self.update_content()
        self.update_ui()

    def set_filter_url(self):
        filter_list = []
        for item in self.filters:
            filter_list.append("%s=%s" % (item["type"], item["id"]))
        self.filter_url = "&".join(filter_list)
        if self.filter_url:
            self.filter_url += "&"

    def set_filter_label(self):
        filter_list = []
        for item in self.filters:
            filter_label = item["label"].decode("utf-8").replace("|", " | ").replace(",", " + ")
            filter_list.append("[COLOR FFAAAAAA]%s:[/COLOR] %s" % (item["typelabel"], filter_label))
        self.filter_label = "  -  ".join(filter_list)

    def update_content(self, add=False, force_update=False):
        if add:
            self.old_items = self.listitems
        else:
            self.old_items = []
        data = self.fetch_data(force=force_update)
        self.listitems = data.get("listitems", [])
        self.total_pages = data.get("results_per_page", "")
        self.total_items = data.get("total_results", "")
        self.next_page_token = data.get("next_page_token", "")
        self.prev_page_token = data.get("prev_page_token", "")
        self.listitems = self.old_items + create_listitems(self.listitems)

    def update_ui(self):
        self.getControl(500).reset()
        self.getControl(500).addItems(self.listitems)
        if self.column is not None:
            self.getControl(500).selectItem(self.column)
        self.window.setProperty("TotalPages", str(self.total_pages))
        self.window.setProperty("TotalItems", str(self.total_items))
        self.window.setProperty("CurrentPage", str(self.page))
        self.window.setProperty("Filter_Label", self.filter_label)
        self.window.setProperty("Sort_Label", self.sort_label)
        if self.page == self.total_pages:
            self.window.clearProperty("ArrowDown")
        else:
            self.window.setProperty("ArrowDown", "True")
        if self.page > 1:
            self.window.setProperty("ArrowUp", "True")
        else:
            self.window.clearProperty("ArrowUp")
        if self.order == "asc":
            self.window.setProperty("Order_Label", LANG(584))
        else:
            self.window.setProperty("Order_Label", LANG(585))

    @busy_dialog
    def update(self, force_update=False):
        self.update_content(force_update=force_update)
        self.update_ui()

    def add_filter(self, key, value, typelabel, label, force_overwrite=False):
        index = -1
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
        if not value:
            return False
        if index > -1:
            self.filters.append(new_filter)
            return None
        if force_overwrite:
            self.filters[index]["id"] = urllib.quote_plus(str(value))
            self.filters[index]["label"] = str(label)
            return None
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno(heading=LANG(587),
                           line1=LANG(32106),
                           nolabel="OR",
                           yeslabel="AND")
        if ret:
            self.filters[index]["id"] = self.filters[index]["id"] + "," + urllib.quote_plus(str(value))
            self.filters[index]["label"] = self.filters[index]["label"] + "," + str(label)
        else:
            self.filters[index]["id"] = self.filters[index]["id"] + "|" + urllib.quote_plus(str(value))
            self.filters[index]["label"] = self.filters[index]["label"] + "|" + str(label)


class DialogBaseInfo(WindowXML if SETTING("window_mode") == "true" else DialogXML):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        super(DialogBaseInfo, self).__init__(*args, **kwargs)
        self.logged_in = check_login()
        self.dbid = kwargs.get('dbid')
        self.data = None
        self.info = {}
        check_version()

    def onInit(self, *args, **kwargs):
        super(DialogBaseInfo, self).onInit()
        HOME.setProperty("ImageColor", self.info.get('ImageColor', ""))
        self.window = xbmcgui.Window(self.window_id)
        self.window.setProperty("tmdb_logged_in", self.logged_in)
        # present for jurialmunkey
        HOME.setProperty("ExtendedInfo_fanart", self.info.get("fanart", ""))

    def fill_lists(self):
        for container_id, listitems in self.listitems:
            try:
                self.getControl(container_id).reset()
                self.getControl(container_id).addItems(listitems)
            except:
                log("Notice: No container with id %i available" % container_id)

    @ch.context(1250)
    def thumbnail_options(self):
        if not self.info.get("dbid"):
            return None
        selection = xbmcgui.Dialog().select(heading=LANG(22080),
                                            list=[LANG(32006)])
        if selection == 0:
            path = self.getControl(focus_id).getSelectedItem().getProperty("original")
            media_type = self.window.getProperty("type")
            params = '"art": {"poster": "%s"}' % path
            get_kodi_json(method="VideoLibrary.Set%sDetails" % media_type,
                          params='{ %s, "%sid":%s }' % (params, media_type.lower(), self.info['dbid']))

    @ch.context(1350)
    def fanart_options(self):
        if not self.info.get("dbid"):
            return None
        selection = xbmcgui.Dialog().select(heading=LANG(22080),
                                            list=[LANG(32007)])
        if selection == 0:
            path = self.getControl(focus_id).getSelectedItem().getProperty("original")
            media_type = self.window.getProperty("type")
            params = '"art": {"fanart": "%s"}' % path
            get_kodi_json(method="VideoLibrary.Set%sDetails" % media_type,
                          params='{ %s, "%sid":%s }' % (params, media_type.lower(), self.info['dbid']))

    def onAction(self, action):
        focus_id = self.getFocusId()
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            wm.pop_stack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()
        if action == xbmcgui.ACTION_CONTEXT_MENU:
            ch.serve_context(focus_id, self)

    def open_credit_dialog(self, credit_id):
        info = get_credit_info(credit_id)
        listitems = []
        if "seasons" in info["media"]:
            listitems += handle_tmdb_seasons(info["media"]["seasons"])
        if "episodes" in info["media"]:
            listitems += handle_tmdb_episodes(info["media"]["episodes"])
        if not listitems:
            listitems += [{"label": LANG(19055)}]
        listitem, index = wm.open_selectdialog(listitems=listitems)
        if listitem["media_type"] == "episode":
            wm.open_episode_info(prev_window=self,
                                 season=listitems[index]["season"],
                                 episode=listitems[index]["episode"],
                                 tvshow_id=info["media"]["id"])
        elif listitem["media_type"] == "season":
            wm.open_season_info(prev_window=self,
                                season=listitems[index]["season"],
                                tvshow_id=info["media"]["id"])
