# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui

from resources.lib.WindowManager import wm

from kodi65 import addon
from kodi65 import utils
from kodi65 import confirmdialog
from T9Search import T9Search
from kodi65.actionhandler import ActionHandler

ch = ActionHandler()

ID_BUTTON_SEARCH = 6000
ID_BUTTON_RESETFILTERS = 5005
ID_BUTTON_PREV_PAGE = 700
ID_BUTTON_NEXT_PAGE = 600


class DialogBaseList(object):

    def __init__(self, *args, **kwargs):
        super(DialogBaseList, self).__init__(*args, **kwargs)
        self.search_str = kwargs.get('search_str', "")
        self.filter_label = kwargs.get("filter_label", "")
        self.mode = kwargs.get("mode", "filter")
        self.order = kwargs.get('order', "desc")
        self.filters = kwargs.get('filters', [])
        self.page = 1
        self.listitems = None
        self.column = None
        self.last_position = 0
        self.total_pages = 1
        self.total_items = 0
        self.page_token = ""
        self.next_page_token = ""
        self.prev_page_token = ""

    def onInit(self):
        super(DialogBaseList, self).onInit()
        self.update_ui()
        if self.total_items > 0:
            self.setFocusId(self.getCurrentContainerId())
            self.setCurrentListPosition(self.last_position)
        else:
            self.setFocusId(ID_BUTTON_SEARCH)

    def close(self):
        self.last_position = self.getCurrentListPosition()
        super(DialogBaseList, self).close()

    @ch.action("parentdir", "*")
    @ch.action("parentfolder", "*")
    def previous_menu(self, control_id):
        onback = self.getProperty("%i_onback" % control_id)
        if onback:
            xbmc.executebuiltin(onback)
        else:
            self.close()
            wm.pop_stack()

    @ch.action("previousmenu", "*")
    def exit_script(self, control_id):
        self.close()

    @ch.action("left", "*")
    @ch.action("right", "*")
    @ch.action("up", "*")
    @ch.action("down", "*")
    def save_position(self, control_id):
        self.position = self.getCurrentListPosition()

    def onAction(self, action):
        ch.serve_action(action, self.getFocusId(), self)

    def onFocus(self, control_id):
        if control_id == ID_BUTTON_NEXT_PAGE:
            self.go_to_next_page()
        elif control_id == ID_BUTTON_PREV_PAGE:
            self.go_to_prev_page()

    @ch.click(ID_BUTTON_RESETFILTERS)
    def reset_filters(self, control_id):
        if len(self.filters) > 1:
            listitems = ["%s: %s" % (f["typelabel"], f["label"]) for f in self.filters]
            listitems.append(addon.LANG(32078))
            index = xbmcgui.Dialog().select(heading=addon.LANG(32077),
                                            list=listitems)
            if index == -1:
                return None
            elif index == len(listitems) - 1:
                self.filters = []
            else:
                del self.filters[index]
        else:
            self.filters = []
        self.reset()

    @ch.click(ID_BUTTON_SEARCH)
    def open_search(self, control_id):
        if addon.bool_setting("classic_search"):
            result = xbmcgui.Dialog().input(heading=addon.LANG(16017),
                                            type=xbmcgui.INPUT_ALPHANUM)
            if result and result > -1:
                self.search(result.decode("utf-8"))
        else:
            T9Search(call=self.search,
                     start_value="",
                     history=self.__class__.__name__ + ".search")
        if self.total_items > 0:
            self.setFocusId(self.getCurrentContainerId())

    def onClick(self, control_id):
        ch.serve(control_id, self)

    def search(self, label):
        if not label:
            return None
        self.search_str = label
        self.filters = []
        self.reset("search")

    def set_filter_label(self):
        filters = []
        for item in self.filters:
            filter_label = item["label"].replace("|", " | ").replace(",", " + ")
            filters.append("[COLOR FFAAAAAA]%s:[/COLOR] %s" % (item["typelabel"], filter_label))
        self.filter_label = "  -  ".join(filters)

    def update_content(self, force_update=False):
        self.data = self.fetch_data(force=force_update)
        if not self.data:
            return None
        self.listitems = self.data.create_listitems()
        self.total_pages = self.data.total_pages
        self.total_items = self.data.totals
        self.next_page_token = self.data.next_page_token
        self.prev_page_token = self.data.prev_page_token

    def update_ui(self):
        if not self.listitems and self.getFocusId() == self.getCurrentContainerId():
            self.setFocusId(ID_BUTTON_SEARCH)
        self.clearList()
        if self.listitems:
            for item in self.listitems:
                self.addItem(item)
            if self.column is not None:
                self.setCurrentListPosition(self.column)
        self.setProperty("TotalPages", str(self.total_pages))
        self.setProperty("TotalItems", str(self.total_items))
        self.setProperty("CurrentPage", str(self.page))
        self.setProperty("Filter_Label", self.filter_label)
        self.setProperty("Sort_Label", self.sort_label)
        self.setProperty("ArrowDown", "True" if self.page != self.total_pages else "")
        self.setProperty("ArrowUp", "True" if self.page > 1 else "")
        self.setProperty("Order_Label", addon.LANG(584) if self.order == "asc" else addon.LANG(585))

    def reset(self, mode="filter"):
        self.page = 1
        self.mode = mode
        self.update()

    def go_to_next_page(self):
        self.get_column()
        if self.page < self.total_pages:
            self.page += 1
            self.prev_page_token = self.page_token
            self.page_token = self.next_page_token
            self.update()

    def go_to_prev_page(self):
        self.get_column()
        if self.page > 1:
            self.page -= 1
            self.next_page_token = self.page_token
            self.page_token = self.prev_page_token
            self.update()

    def get_column(self):
        for i in xrange(0, 10):
            if xbmc.getCondVisibility("Container(500).Column(%i)" % i):
                self.column = i
                break

    @utils.busy_dialog
    def update(self, force_update=False):
        self.update_content(force_update=force_update)
        self.update_ui()

    def add_filter(self, key, value, typelabel, label, force_overwrite=False, reset=True):
        if not value:
            return False
        new_filter = {"id": str(value),
                      "type": key,
                      "typelabel": typelabel,
                      "label": label}
        if new_filter in self.filters:
            return False
        index = -1
        for i, item in enumerate(self.filters):
            if item["type"] == key:
                index = i
                break
        if index == -1:
            self.filters.append(new_filter)
            if reset:
                self.reset()
            return None
        if force_overwrite:
            self.filters[index]["id"] = str(value)
            self.filters[index]["label"] = str(label)
            if reset:
                self.reset()
            return None
        ret = confirmdialog.open(header=addon.LANG(587),
                                 text=addon.LANG(32106),
                                 nolabel="OR",
                                 yeslabel="AND")
        if ret == -1:
            return None
        if ret == 1:
            self.filters[index]["id"] += ",%s" % value
            self.filters[index]["label"] += ",%s" % label
        elif ret == 0:
            self.filters[index]["id"] += "|%s" % value
            self.filters[index]["label"] += "|%s" % label
        if reset:
            self.reset()
