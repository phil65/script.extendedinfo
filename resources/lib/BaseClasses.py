# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from TheMovieDB import *


class DialogBaseList(xbmcgui.WindowXMLDialog if not ADDON.getSetting("window_mode") == "true" else xbmcgui.WindowXML):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listitem_list = kwargs.get('listitems', None)
        self.color = kwargs.get('color', "FFAAAAAA")
        self.page = 1
        self.total_pages = 1
        self.total_items = 0
        check_version()

    def onInit(self):
        HOME.setProperty("WindowColor", self.color)
        if not ADDON.getSetting("window_mode") == "true":
            self.window_id = xbmcgui.getCurrentWindowDialogId()
        else:
            self.window_id = xbmcgui.getCurrentWindowId()
        self.window = xbmcgui.Window(self.window_id)
        self.window.setProperty("WindowColor", self.color)
        self.window.setProperty("layout", self.layout)
        self.update_ui()
        xbmc.sleep(200)
        if self.total_items > 0:
            xbmc.executebuiltin("SetFocus(500)")
        else:
            xbmc.executebuiltin("SetFocus(6000)")

    def search(self, label):
        self.search_string = label
        self.mode = "search"
        self.filters = []
        self.page = 1
        self.update_content()
        self.update_ui()

    def set_filter_url(self):
        filter_list = []
        # prettyprint(self.filters)
        for item in self.filters:
            filter_list.append("%s=%s" % (item["type"], item["id"]))
        self.filter_url = "&".join(filter_list)
        if self.filter_url:
            self.filter_url += "&"

    def set_filter_label(self):
        filter_list = []
        # prettyprint(self.filters)
        for item in self.filters:
            filter_list.append("[COLOR FFAAAAAA]%s:[/COLOR] %s" % (item["typelabel"], item["label"].decode("utf-8").replace("|", " | ").replace(",", " + ")))
        self.filter_label = "  -  ".join(filter_list)

    def update_content(self, add=False, force_update=False):
        if add:
            self.old_items = self.listitems
        else:
            self.old_items = []
        self.listitems, self.total_pages, self.total_items = self.fetch_data(force=force_update)
        self.listitems = self.old_items + create_listitems(self.listitems)

    def update_ui(self):
        self.getControl(500).reset()
        self.getControl(500).addItems(self.listitems)
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
            self.window.setProperty("Order_Label", xbmc.getLocalizedString(584))
        else:
            self.window.setProperty("Order_Label", xbmc.getLocalizedString(585))

    @busy_dialog
    def onFocus(self, control_id):
        if control_id == 600:
            if self.page < self.total_pages:
                self.page += 1
            else:
                self.page = 1
                return
            self.update_content()
            self.update_ui()
        if control_id == 700:
            if self.page > 1:
                self.page -= 1
            else:
                return
            # else:
            #     self.page = self.total_pages
            self.update_content()
            self.update_ui()

    def onClick(self, control_id):
        if control_id == 5001:
            self.get_sort_type()
            self.update_content()
            self.update_ui()

    def add_filter(self, key, value, typelabel, label):
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
            if not self.force_overwrite:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno(heading=xbmc.getLocalizedString(587), line1=ADDON.getLocalizedString(32106), nolabel="OR", yeslabel="AND")
                if ret:
                    self.filters[index]["id"] = self.filters[index]["id"] + "," + urllib.quote_plus(str(value))
                    self.filters[index]["label"] = self.filters[index]["label"] + "," + str(label)
                else:
                    self.filters[index]["id"] = self.filters[index]["id"] + "|" + urllib.quote_plus(str(value))
                    self.filters[index]["label"] = self.filters[index]["label"] + "|" + str(label)
            else:
                self.filters[index]["id"] = urllib.quote_plus(str(value))
                self.filters[index]["label"] = str(label)
        else:
            self.filters.append(new_filter)


class DialogBaseInfo(xbmcgui.WindowXMLDialog if not ADDON.getSetting("window_mode") == "true" else xbmcgui.WindowXML):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.logged_in = check_login()
        self.movieplayer = VideoPlayer(pop_stack=True)
        self.data = None
        check_version()

    def onInit(self, *args, **kwargs):
        if not ADDON.getSetting("window_mode") == "true":
            self.window_id = xbmcgui.getCurrentWindowDialogId()
        else:
            self.window_id = xbmcgui.getCurrentWindowId()
        self.window = xbmcgui.Window(self.window_id)
        self.window.setProperty("tmdb_logged_in", self.logged_in)
        if not self.data:
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.close()
            return

    def fill_lists(self):
        for container_id, listitems in self.listitems:
            try:
                self.getControl(container_id).reset()
                self.getControl(container_id).addItems(listitems)
            except:
                log("Notice: No container with id %i available" % container_id)

    def onAction(self, action):
        focus_id = self.getFocusId()
        control = self.getControl(focus_id)
        media_type = self.window.getProperty("type")
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            pop_window_stack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()
        if action == xbmcgui.ACTION_CONTEXT_MENU:
            if focus_id == 1250 and self.data["general"].get("DBID"):
                selection = xbmcgui.Dialog().select(xbmc.getLocalizedString(22080), ["Use as thumbnail"])
                if selection == 0:
                    path = control.getSelectedItem().getProperty("original")
                    params = '"art": {"poster": "%s"}' % path
                    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.Set%sDetails", "params": { %s, "%sid":%s }}' % (media_type, params, media_type.lower(), self.data["general"]['DBID']))
            elif focus_id == 1350 and self.data["general"].get("DBID"):
                selection = xbmcgui.Dialog().select(xbmc.getLocalizedString(22080), ["Use as fanart"])
                if selection == 0:
                    path = control.getSelectedItem().getProperty("original")
                    params = '"art": {"fanart": "%s"}' % path
                    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.Set%sDetails", "params": { %s, "%sid":%s }}' % (media_type, params, media_type.lower(), self.data["general"]['DBID']))

    def open_video_list(self, listitems=None, filters=[], mode="filter", list_id=False, filter_label="", force=False, media_type="movie"):
        import DialogVideoList
        add_to_window_stack(self)
        self.close()
        dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % ADDON_NAME, ADDON_PATH, listitems=listitems, color=self.data["general"]['ImageColor'], filters=filters, mode=mode, list_id=list_id, force=force, filter_label=filter_label, type=media_type)
        dialog.doModal()
