# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import time
from threading import Timer
import xbmcgui
from Utils import *


class T9Search(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        self.callback = kwargs.get("call")
        self.search_str = kwargs.get("start_value", "")
        self.last_searches = kwargs.get("history", "")
        self.previous = False
        self.prev_time = 0
        self.timer = None
        self.color_timer = None

    def onInit(self):
        self.get_autocomplete_labels_async()
        self.classic_mode = False
        self.update_search_label_async()
        keys = (("1", "ABC1"),
                ("2", "DEF2"),
                ("3", "GHI3"),
                ("4", "JKL4"),
                ("5", "MNO5"),
                ("6", "PQR6"),
                ("7", "STU7"),
                ("8", "VWX8"),
                ("9", "YZ90"),
                ("DEL", "<--"),
                ("", "___"),
                ("KEYB", "CLASSIC"))
        listitems = []
        for item in keys:
            li = xbmcgui.ListItem("[B]%s[/B]" % item[0], item[1])
            li.setProperty("key", item[0])
            li.setProperty("value", item[1])
            listitems.append(li)
        self.getControl(9090).addItems(listitems)
        self.setFocusId(9090)
        self.getControl(600).setLabel("[B]%s[/B]_" % self.search_str)

    @run_async
    def update_search_label_async(self):
        while True:
            time.sleep(1)
            if int(time.time()) % 2 == 0:
                self.getControl(600).setLabel("[B]%s[/B]_" % self.search_str)
            else:
                self.getControl(600).setLabel("[B]%s[/B][COLOR 00FFFFFF]_[/COLOR]" % self.search_str)

    def onClick(self, control_id):
        if control_id == 9090:
            letters = self.getControl(9090).getSelectedItem().getProperty("value")
            number = self.getControl(9090).getSelectedItem().getProperty("key")
            letter_list = [c for c in letters]
            now = time.time()
            time_diff = now - self.prev_time
            if number == "DEL":
                if self.search_str:
                    self.search_str = self.search_str[:-1]
            elif number == "":
                if self.search_str:
                    self.search_str += " "
            elif number == "KEYB":
                self.classic_mode = True
                self.close()
            elif self.previous != letters or time_diff >= 1:
                self.prev_time = now
                self.previous = letters
                self.search_str += letter_list[0]
                self.color_labels(letter_list[0], letters)
            elif time_diff < 1:
                if self.color_timer:
                    self.color_timer.cancel()
                self.prev_time = now
                idx = (letter_list.index(self.search_str[-1]) + 1) % len(letter_list)
                self.search_str = self.search_str[:-1] + letter_list[idx]
                self.color_labels(letter_list[idx], letters)
            if self.timer:
                self.timer.cancel()
            self.timer = Timer(1.0, self.callback, (self.search_str,))
            self.timer.start()
            self.getControl(600).setLabel("[B]%s[/B]_" % self.search_str)
            self.get_autocomplete_labels_async()
        elif control_id == 9091:
            self.search_str = self.getControl(9091).getSelectedItem().getLabel()
            self.getControl(600).setLabel("[B]%s[/B]_" % self.search_str)
            self.get_autocomplete_labels_async()
            if self.timer:
                self.timer.cancel()
            self.timer = Timer(0.0, self.callback, (self.search_str,))
            self.timer.start()

    def color_labels(self, letter, letters):
        label = "[COLOR=FFFF3333]%s[/COLOR]" % letter
        self.getControl(9090).getSelectedItem().setLabel2(letters.replace(letter, label))
        self.color_timer = Timer(1.0, self.reset_color, (self.getControl(9090).getSelectedItem(),))
        self.color_timer.start()

    def reset_color(self, item):
        label = item.getLabel2()
        label = label.replace("[COLOR=FFFF3333]", "").replace("[/COLOR]", "")
        item.setLabel2(label)

    @run_async
    def get_autocomplete_labels_async(self):
        self.getControl(9091).reset()
        if self.search_str:
            listitems = get_autocomplete_items(self.search_str)
        else:
            listitems = list(self.last_searches)
        self.getControl(9091).addItems(create_listitems(listitems))
