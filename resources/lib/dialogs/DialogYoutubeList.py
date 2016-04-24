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
from kodi65.actionhandler import ActionHandler

ch = ActionHandler()

ID_BUTTON_SORTTYPE = 5001
ID_BUTTON_PUBLISHEDFILTER = 5002
ID_BUTTON_LANGUAGEFILTER = 5003
ID_BUTTON_DIMENSIONFILTER = 5006
ID_BUTTON_TOGGLETYPE = 5007
ID_BUTTON_DURATIONFILTER = 5008
ID_BUTTON_CAPTIONFILTER = 5009
ID_BUTTON_DEFINITIONFILTER = 5012


def get_window(window_type):

    class DialogYoutubeList(DialogBaseList, window_type):

        FILTERS = {"channelId": addon.LANG(19029),
                   "publishedAfter": addon.LANG(172),
                   "regionCode": addon.LANG(248),
                   "videoDimension": addon.LANG(32057),
                   "videoDuration": addon.LANG(180),
                   "videoCaption": addon.LANG(287),
                   "videoDefinition": addon.LANG(32058),
                   "relatedToVideoId": addon.LANG(32058),
                   "channelId": addon.LANG(19029)}

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

        @utils.busy_dialog
        def __init__(self, *args, **kwargs):
            self.type = kwargs.get('type', "video")
            super(DialogYoutubeList, self).__init__(*args, **kwargs)

        def onClick(self, control_id):
            super(DialogYoutubeList, self).onClick(control_id)
            ch.serve(control_id, self)

        def onAction(self, action):
            super(DialogYoutubeList, self).onAction(action)
            ch.serve_action(action, self.getFocusId(), self)

        @ch.click_by_type("video")
        def main_list_click(self, control_id):
            youtube_id = self.FocusedItem(control_id).getProperty("youtube_id")
            media_type = self.FocusedItem(control_id).getProperty("type")
            if media_type == "channel":
                channel_filter = [{"id": youtube_id,
                                   "type": "channelId",
                                   "label": self.FocusedItem(control_id).getLabel().decode("utf-8")}]
                wm.open_youtube_list(filters=channel_filter)
            else:
                wm.play_youtube_video(youtube_id=youtube_id,
                                      listitem=self.FocusedItem(control_id))

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
                            label=labels[index])

        def chooose_filter(self, filter_code, header, options):
            values = [i[0] for i in options]
            labels = [i[1] for i in options]
            index = xbmcgui.Dialog().select(heading=addon.LANG(header),
                                            list=labels)
            if index == -1:
                return None
            self.add_filter(key=filter_code,
                            value=values[index],
                            label=labels[index])

        @ch.click(ID_BUTTON_LANGUAGEFILTER)
        def set_language_filter(self, control_id):
            options = [("en", "en"),
                       ("de", "de"),
                       ("fr", "fr")]
            self.chooose_filter("regionCode", 32151, options)

        @ch.click(ID_BUTTON_DIMENSIONFILTER)
        def set_dimension_filter(self, control_id):
            options = [("2d", "2D"),
                       ("3d", "3D"),
                       ("any", addon.LANG(593))]
            self.chooose_filter("videoDimension", 32151, options)

        @ch.click(ID_BUTTON_DURATIONFILTER)
        def set_duration_filter(self, control_id):
            options = [("long", addon.LANG(33013)),
                       ("medium", addon.LANG(601)),
                       ("short", addon.LANG(33012)),
                       ("any", addon.LANG(593))]
            self.chooose_filter("videoDuration", 32151, options)

        @ch.click(ID_BUTTON_CAPTIONFILTER)
        def set_caption_filter(self, control_id):
            options = [("closedCaption", addon.LANG(107)),
                       ("none", addon.LANG(106)),
                       ("any", addon.LANG(593))]
            self.chooose_filter("videoCaption", 287, options)

        @ch.click(ID_BUTTON_DEFINITIONFILTER)
        def set_definition_filter(self, control_id):
            options = [("high", addon.LANG(419)),
                       ("standard", addon.LANG(602)),
                       ("any", addon.LANG(593))]
            self.chooose_filter("videoDefinition", 169, options)

        @ch.click(ID_BUTTON_TOGGLETYPE)
        def toggle_type(self, control_id):
            self.filters = []
            types = {"video": "playlist",
                     "playlist": "channel",
                     "channel": "video"}
            if self.type in types:
                self.type = types[self.type]
            if self.sort not in self.SORTS[self.type].keys():
                self.set_sort("relevance")
            self.reset()

        def update_ui(self):
            self.getControl(ID_BUTTON_DIMENSIONFILTER).setVisible(self.type == "video")
            self.getControl(ID_BUTTON_DURATIONFILTER).setVisible(self.type == "video")
            self.getControl(ID_BUTTON_CAPTIONFILTER).setVisible(self.type == "video")
            self.getControl(ID_BUTTON_DEFINITIONFILTER).setVisible(self.type == "video")
            super(DialogYoutubeList, self).update_ui()

        def get_default_sort(self):
            return "relevance"

        @ch.click(ID_BUTTON_SORTTYPE)
        def get_sort_type(self, control_id):
            if not self.choose_sort_method(self.type):
                return None
            self.update()

        @ch.context("video")
        def context_menu(self, control_id):
            if self.type == "video":
                more_vids = "%s [B]%s[/B]" % (addon.LANG(32081), self.FocusedItem(control_id).getProperty("channel_title"))
                index = xbmcgui.Dialog().contextmenu(list=[addon.LANG(32069), more_vids])
                if index < 0:
                    return None
                elif index == 0:
                    filter_ = [{"id": self.FocusedItem(control_id).getProperty("youtube_id"),
                                "type": "relatedToVideoId",
                                "label": self.FocusedItem(control_id).getLabel()}]
                    wm.open_youtube_list(filters=filter_)
                elif index == 1:
                    filter_ = [{"id": self.FocusedItem(control_id).getProperty("channel_id"),
                                "type": "channelId",
                                "label": self.FocusedItem(control_id).getProperty("channel_title")}]
                    wm.open_youtube_list(filters=filter_)

        def add_filter(self, **kwargs):
            kwargs["typelabel"] = self.FILTERS[kwargs["key"]]
            super(DialogYoutubeList, self).add_filter(force_overwrite=True,
                                                      **kwargs)

        def fetch_data(self, force=False):
            self.set_filter_label()
            if self.search_str:
                self.filter_label = addon.LANG(32146) % (self.search_str) + "  " + self.filter_label
            return YouTube.search(search_str=self.search_str,
                                  orderby=self.sort,
                                  extended=True,
                                  filters={item["type"]: item["id"] for item in self.filters},
                                  media_type=self.type,
                                  page=self.page_token)

    return DialogYoutubeList
