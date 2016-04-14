# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcgui

from DialogBaseInfo import DialogBaseInfo

from kodi65 import addon
from ActionHandler import ActionHandler


BUTTONS = [8, 9, 10, 445, 6001, 6002, 6003, 6005, 6006]

ch = ActionHandler()


class DialogVideoInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogVideoInfo, self).__init__(*args, **kwargs)

    def onClick(self, control_id):
        super(DialogVideoInfo, self).onClick(control_id)
        ch.serve(control_id, self)

    def set_buttons(self):
        for button_id in BUTTONS:
            self.set_visible(button_id, False)

    @ch.click(132)
    def show_plot(self, control_id):
        xbmcgui.Dialog().textviewer(heading=addon.LANG(207),
                                    text=self.info.get_info("plot"))


