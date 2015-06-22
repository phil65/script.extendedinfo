# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from YouTube import *
from BaseClasses import DialogBaseList

TRANSLATIONS = {"video": xbmc.getLocalizedString(157),
                "playlist": xbmc.getLocalizedString(559),
                "channel": xbmc.getLocalizedString(19029)}
SORTS = {"video": {xbmc.getLocalizedString(552): "date",
                   xbmc.getLocalizedString(563): "rating",
                   ADDON.getLocalizedString(32060): "relevance",
                   xbmc.getLocalizedString(369): "title",
                   xbmc.getLocalizedString(567): "viewCount"},
         "playlist": {xbmc.getLocalizedString(552): "date",
                      xbmc.getLocalizedString(563): "rating",
                      ADDON.getLocalizedString(32060): "relevance",
                      xbmc.getLocalizedString(369): "title",
                      ADDON.getLocalizedString(32068): "videoCount",
                      xbmc.getLocalizedString(567): "viewCount"},
         "channel": {xbmc.getLocalizedString(552): "date",
                     xbmc.getLocalizedString(563): "rating",
                     ADDON.getLocalizedString(32060): "relevance",
                     xbmc.getLocalizedString(369): "title",
                     ADDON.getLocalizedString(32068): "videoCount",
                     xbmc.getLocalizedString(567): "viewCount"}}


class DialogYoutubeList(DialogBaseList):

    def __init__(self, *args, **kwargs):
        super(DialogYoutubeList, self).__init__(*args, **kwargs)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.type = kwargs.get('type', "video")
        self.search_string = kwargs.get('search_string', "")
        self.filter_label = kwargs.get("filter_label", "")
        self.filter_url = ""
        self.mode = kwargs.get("mode", "filter")
        self.sort = kwargs.get('sort', "relevance")
        self.sort_label = kwargs.get('sort_label', ADDON.getLocalizedString(32060))
        self.order = kwargs.get('order', "desc")
        force = kwargs.get('force', False)
        self.filters = kwargs.get('filters', [])
        if self.listitem_list:
            self.listitems = create_listitems(self.listitem_list)
            self.total_items = len(self.listitem_list)
        else:
            self.update_content(force_update=force)
            # notify(str(self.totalpages))
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onClick(self, control_id):
        super(DialogYoutubeList, self).onClick(control_id)
        if control_id in [500]:
            self.last_position = self.getControl(control_id).getSelectedPosition()
            youtube_id = self.getControl(control_id).getSelectedItem().getProperty("youtube_id")
            if youtube_id:
                PLAYER.playYoutubeVideo(youtube_id, self.getControl(control_id).getSelectedItem(), window=self)
        elif control_id == 5002:
            label_list = [ADDON.getLocalizedString(32062), ADDON.getLocalizedString(32063), ADDON.getLocalizedString(32064), ADDON.getLocalizedString(32065), xbmc.getLocalizedString(636)]
            deltas = [1, 7, 31, 365, "custom"]
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), label_list)
            if index > -1:
                delta = deltas[index]
                if delta == "custom":
                    delta = xbmcgui.Dialog().input(ADDON.getLocalizedString(32067), "", type=xbmcgui.INPUT_NUMERIC)
                if delta:
                    d = datetime.datetime.now() - datetime.timedelta(int(delta))
                    date_string = d.isoformat('T')[:-7] + "Z"
                    self.add_filter("publishedAfter", date_string, xbmc.getLocalizedString(172), str(label_list[index]))
                    self.update()
        elif control_id == 5003:
            label_list = ["en", "de", "fr"]
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), label_list)
            if index > -1:
                self.add_filter("regionCode", label_list[index], xbmc.getLocalizedString(248), str(label_list[index]))
                self.update()
        elif control_id == 5006:
            value_list = ["2d", "3d", "any"]
            label_list = ["2d", "3d", xbmc.getLocalizedString(593)]
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), label_list)
            if index > -1:
                self.add_filter("videoDimension", value_list[index], "Dimensions", str(label_list[index]))
                self.update()
        elif control_id == 5008:
            value_list = ["long", "medium", "short", "any"]
            label_list = [xbmc.getLocalizedString(33013), xbmc.getLocalizedString(601), xbmc.getLocalizedString(33012), xbmc.getLocalizedString(593)]
            index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), label_list)
            if index > -1:
                self.add_filter("videoDuration", value_list[index], xbmc.getLocalizedString(180), str(label_list[index]))
                self.update()
        elif control_id == 5009:
            value_list = ["closedCaption", "none", "any"]
            label_list = [xbmc.getLocalizedString(107), xbmc.getLocalizedString(106), xbmc.getLocalizedString(593)]
            index = xbmcgui.Dialog().select(xbmc.getLocalizedString(287), label_list)
            if index > -1:
                self.add_filter("videoCaption", value_list[index], xbmc.getLocalizedString(287), str(label_list[index]))
                self.update()
        elif control_id == 5012:
            value_list = ["high", "standard", "any"]
            label_list = [xbmc.getLocalizedString(419), xbmc.getLocalizedString(602), xbmc.getLocalizedString(593)]
            index = xbmcgui.Dialog().select(xbmc.getLocalizedString(169), label_list)
            if index > -1:
                self.add_filter("videoDefinition", value_list[index], xbmc.getLocalizedString(169), str(label_list[index]))
                self.update()
        elif control_id == 5007:
            self.filters = []
            self.page = 1
            self.mode = "filter"
            if self.type == "video":
                self.type = "playlist"
            elif self.type == "playlist":
                self.type = "channel"
            elif self.type == "channel":
                self.type = "video"
            if self.sort not in SORTS[self.type].values():
                self.sort = "relevance"
                self.sort_label = ADDON.getLocalizedString(32060)
            self.update()

    def update_ui(self):
        self.window.setProperty("Type", TRANSLATIONS[self.type])
        if self.type == "video":
            self.window.getControl(5004).setVisible(False)
            self.window.getControl(5006).setVisible(True)
            self.window.getControl(5008).setVisible(True)
            self.window.getControl(5009).setVisible(True)
            self.window.getControl(5010).setVisible(False)
            self.window.getControl(5012).setVisible(True)
        elif self.type == "playlist":
            self.window.getControl(5004).setVisible(False)
            self.window.getControl(5006).setVisible(False)
            self.window.getControl(5008).setVisible(False)
            self.window.getControl(5009).setVisible(False)
            self.window.getControl(5010).setVisible(False)
            self.window.getControl(5012).setVisible(False)
        elif self.type == "channel":
            self.window.getControl(5004).setVisible(False)
            self.window.getControl(5006).setVisible(False)
            self.window.getControl(5008).setVisible(False)
            self.window.getControl(5009).setVisible(False)
            self.window.getControl(5010).setVisible(False)
            self.window.getControl(5012).setVisible(False)
        super(DialogYoutubeList, self).update_ui()

    def go_to_next_page(self):
        if self.page < self.total_pages:
            self.page += 1

    def go_to_prev_page(self):
        if self.page > 1:
            self.page -= 1

    def get_sort_type(self):
        listitems = []
        sort_strings = []
        sort_key = self.type
        for (key, value) in SORTS[sort_key].iteritems():
            listitems.append(key)
            sort_strings.append(value)
        index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32104), listitems)
        if index > -1:
            self.sort = sort_strings[index]
            self.sort_label = listitems[index]

    def context_menu(self):
        focus_id = self.getFocusId()
        if not focus_id == 500:
            return None
        item_id = self.getControl(focus_id).getSelectedItem().getProperty("id")

    def add_filter(self, key, value, typelabel, label):
        super(DialogYoutubeList, self).add_filter(key, value, typelabel, label, force_overwrite=True)
        self.mode = "filter"
        self.page = 1

    def fetch_data(self, force=False):
        self.set_filter_url()
        self.set_filter_label()
        if self.search_string:
            self.filter_label = ADDON.getLocalizedString(32146) % (self.search_string) + "  " + self.filter_label
        else:
            self.filter_label = self.filter_label
        return get_youtube_search_videos(self.search_string, orderby=self.sort, extended=True, filter_string=self.filter_url, item_info=True, media_type=self.type, page=self.page)
