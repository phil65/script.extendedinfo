# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import datetime

import xbmcgui

from resources.lib import YouTube
from resources.lib.WindowManager import wm
from DialogBaseList import DialogBaseList

from kodi65 import addon
from kodi65 import utils
from ActionHandler import ActionHandler

ch = ActionHandler()

ID_MAIN_LIST = 500
ID_BUTTON_SORTTYPE = 5001
ID_BUTTON_PUBLISHEDFILTER = 5002
ID_BUTTON_LANGUAGEFILTER = 5003
ID_BUTTON_DIMENSIONFILTER = 5006
ID_BUTTON_TOGGLETYPE = 5007
ID_BUTTON_DURATIONFILTER = 5008
ID_BUTTON_CAPTIONFILTER = 5009
ID_BUTTON_DEFINITIONFILTER = 5012

TRANSLATIONS = {"video": addon.LANG(157),
                "playlist": addon.LANG(559),
                "channel": addon.LANG(19029)}

SORTS = {"video": {"date": addon.LANG(552),
                   "rating": addon.LANG(563),
                   "relevance": addon.LANG(32060),
                   "title": addon.LANG(369),
                   "viewCount": addon.LANG(567)},
         "playlist": {"date": addon.LANG(552),
                      "rating": addon.LANG(563),
                      "relevance": addon.LANG(32060),
                      "title": addon.LANG(369),
                      "videoCount": addon.LANG(32068),
                      "viewCount": addon.LANG(567)},
         "channel": {"date": addon.LANG(552),
                     "rating": addon.LANG(563),
                     "relevance": addon.LANG(32060),
                     "title": addon.LANG(369),
                     "videoCount": addon.LANG(32068),
                     "viewCount": addon.LANG(567)}}


def get_window(window_type):

    class DialogYoutubeList(DialogBaseList, window_type):

        @utils.busy_dialog
        def __init__(self, *args, **kwargs):
            super(DialogYoutubeList, self).__init__(*args, **kwargs)
            self.type = kwargs.get('type', "video")
            self.sort = kwargs.get('sort', "relevance")
            self.sort_label = kwargs.get('sort_label', addon.LANG(32060))
            self.order = kwargs.get('order', "desc")
            force = kwargs.get('force', False)
            self.update_content(force_update=force)

        def onClick(self, control_id):
            super(DialogYoutubeList, self).onClick(control_id)
            ch.serve(control_id, self)

        def onAction(self, action):
            super(DialogYoutubeList, self).onAction(action)
            ch.serve_action(action, self.getFocusId(), self)

        @ch.click(ID_MAIN_LIST)
        def main_list_click(self, control_id):
            self.last_position = self.getControl(control_id).getSelectedPosition()
            youtube_id = self.FocusedItem(control_id).getProperty("youtube_id")
            if self.type == "channel":
                channel_filter = [{"id": youtube_id,
                                   "type": "channelId",
                                   "typelabel": addon.LANG(19029),
                                   "label": youtube_id}]
                wm.open_youtube_list(filters=channel_filter)
            else:
                wm.play_youtube_video(youtube_id=youtube_id,
                                      listitem=self.FocusedItem(control_id),
                                      window=self)

        @ch.click(ID_BUTTON_PUBLISHEDFILTER)
        def set_published_filter(self, control_id):
            labels = [addon.LANG(32062), addon.LANG(32063), addon.LANG(32064), addon.LANG(32065), addon.LANG(636)]
            deltas = [1, 7, 31, 365, "custom"]
            index = xbmcgui.Dialog().select(heading=addon.LANG(32151),
                                            list=labels)
            if index == -1:
                return None
            delta = deltas[index]
            if delta == "custom":
                delta = xbmcgui.Dialog().input(heading=addon.LANG(32067),
                                               type=xbmcgui.INPUT_NUMERIC)
            if not delta:
                return None
            d = datetime.datetime.now() - datetime.timedelta(int(delta))
            self.add_filter(key="publishedAfter",
                            value=d.isoformat('T')[:-7] + "Z",
                            typelabel=addon.LANG(172),
                            label=str(labels[index]))

        @ch.click(ID_BUTTON_LANGUAGEFILTER)
        def set_language_filter(self, control_id):
            labels = ["en", "de", "fr"]
            index = xbmcgui.Dialog().select(heading=addon.LANG(32151),
                                            list=labels)
            if index == -1:
                return None
            self.add_filter(key="regionCode",
                            value=labels[index],
                            typelabel=addon.LANG(248),
                            label=str(labels[index]))

        @ch.click(ID_BUTTON_DIMENSIONFILTER)
        def set_dimension_filter(self, control_id):
            values = ["2d", "3d", "any"]
            labels = ["2D", "3D", addon.LANG(593)]
            index = xbmcgui.Dialog().select(heading=addon.LANG(32151),
                                            list=labels)
            if index > -1:
                self.add_filter(key="videoDimension",
                                value=values[index],
                                typelabel="Dimensions",
                                label=str(labels[index]))

        @ch.click(ID_BUTTON_DURATIONFILTER)
        def set_duration_filter(self, control_id):
            values = ["long", "medium", "short", "any"]
            labels = [addon.LANG(33013), addon.LANG(601), addon.LANG(33012), addon.LANG(593)]
            index = xbmcgui.Dialog().select(heading=addon.LANG(32151),
                                            list=labels)
            if index > -1:
                self.add_filter(key="videoDuration",
                                value=values[index],
                                typelabel=addon.LANG(180),
                                label=str(labels[index]))

        @ch.click(ID_BUTTON_CAPTIONFILTER)
        def set_caption_filter(self, control_id):
            values = ["closedCaption", "none", "any"]
            labels = [addon.LANG(107), addon.LANG(106), addon.LANG(593)]
            index = xbmcgui.Dialog().select(heading=addon.LANG(287),
                                            list=labels)
            if index > -1:
                self.add_filter(key="videoCaption",
                                value=values[index],
                                typelabel=addon.LANG(287),
                                label=str(labels[index]))

        @ch.click(ID_BUTTON_DEFINITIONFILTER)
        def set_definition_filter(self, control_id):
            values = ["high", "standard", "any"]
            labels = [addon.LANG(419), addon.LANG(602), addon.LANG(593)]
            index = xbmcgui.Dialog().select(heading=addon.LANG(169),
                                            list=labels)
            if index > -1:
                self.add_filter(key="videoDefinition",
                                value=values[index],
                                typelabel=addon.LANG(169),
                                label=str(labels[index]))

        @ch.click(ID_BUTTON_TOGGLETYPE)
        def toggle_type(self, control_id):
            self.filters = []
            types = {"video": "playlist",
                     "playlist": "channel",
                     "channel": "video"}
            if self.type in types:
                self.type = types[self.type]
            if self.sort not in SORTS[self.type].keys():
                self.sort = "relevance"
                self.sort_label = addon.LANG(32060)
            self.reset()

        def update_ui(self, control_id):
            self.setProperty("Type", TRANSLATIONS[self.type])
            self.getControl(ID_BUTTON_DIMENSIONFILTER).setVisible(self.type == "video")
            self.getControl(ID_BUTTON_DURATIONFILTER).setVisible(self.type == "video")
            self.getControl(ID_BUTTON_CAPTIONFILTER).setVisible(self.type == "video")
            self.getControl(ID_BUTTON_DEFINITIONFILTER).setVisible(self.type == "video")
            super(DialogYoutubeList, self).update_ui()

        @ch.click(ID_BUTTON_SORTTYPE)
        def get_sort_type(self, control_id):
            listitems = [key for key in SORTS[self.type].values()]
            sort_strings = [value for value in SORTS[self.type].keys()]
            index = xbmcgui.Dialog().select(heading=addon.LANG(32104),
                                            list=listitems)
            if index == -1:
                return None
            self.sort = sort_strings[index]
            self.sort_label = listitems[index]
            self.update()

        @ch.action("contextmenu", ID_MAIN_LIST)
        def context_menu(self, control_id):
            if self.type == "video":
                more_vids = "%s [B]%s[/B]" % (addon.LANG(32081), self.FocusedItem(control_id).getProperty("channel_title"))
                selection = xbmcgui.Dialog().contextmenu(heading=addon.LANG(32151),
                                                         list=[addon.LANG(32069), more_vids])
                if selection < 0:
                    return None
                elif selection == 0:
                    filter_ = [{"id": self.FocusedItem(control_id).getProperty("youtube_id"),
                                "type": "relatedToVideoId",
                                "typelabel": "Related",
                                "label": self.FocusedItem(control_id).getLabel()}]
                    wm.open_youtube_list(filters=filter_)
                elif selection == 1:
                    filter_ = [{"id": self.FocusedItem(control_id).getProperty("channel_id"),
                                "type": "channelId",
                                "typelabel": "Related",
                                "label": self.FocusedItem(control_id).getProperty("channel_title")}]
                    wm.open_youtube_list(filters=filter_)

        def add_filter(self, **kwargs):
            super(DialogYoutubeList, self).add_filter(force_overwrite=True,
                                                      **kwargs)

        def fetch_data(self, force=False):
            self.set_filter_label()
            if self.search_str:
                self.filter_label = addon.LANG(32146) % (self.search_str) + "  " + self.filter_label
            else:
                self.filter_label = self.filter_label
            return YouTube.search(self.search_str,
                                  orderby=self.sort,
                                  extended=True,
                                  filters={item["type"]: item["id"] for item in self.filters},
                                  media_type=self.type,
                                  page=self.page_token)

    return DialogYoutubeList
