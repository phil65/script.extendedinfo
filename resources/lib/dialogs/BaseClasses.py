# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcgui


class WindowXML(xbmcgui.WindowXML):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self)
        self.window_type = "window"

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowId()

    def FocusedItem(self, control_id):
        try:
            control = self.getControl(control_id)
            listitem = control.getSelectedItem()
            if not listitem:
                listitem = self.getListItem(self.getCurrentListPosition())
            return listitem
        except Exception:
            return None


class DialogXML(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.window_type = "dialog"

    def onInit(self):
        self.window_id = xbmcgui.getCurrentWindowDialogId()

    def FocusedItem(self, control_id):
        try:
            listitem = self.getControl(control_id).getSelectedItem()
            if not listitem:
                listitem = self.getListItem(self.getCurrentListPosition())
            return listitem
        except Exception:
            return None
