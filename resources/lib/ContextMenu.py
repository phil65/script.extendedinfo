#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2014 Philipp Temminghoff (philipptemminghoff@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import xbmcgui


class ContextMenu(xbmcgui.WindowXMLDialog):

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.labels = kwargs["labels"]

    def onInit(self):
        self._show_context_menu()

    def _show_context_menu(self):
        self._hide_buttons()
        self._setup_menu()
        self.setFocus(self.getControl(1001))

    def _hide_buttons(self):
        for button in range(1001, 1008):
            self.getControl(button).setVisible(False)

    def _setup_menu(self):
        dialog_posx, dialog_posy = self.getControl(999).getPosition()
        dialog_height = self.getControl(999).getHeight()
        button_posx, button_posy = self.getControl(1001).getPosition()
        button_height = self.getControl(1001).getHeight()
        extra_height = (len(self.labels) - 1) * button_height
        dialog_height = dialog_height + extra_height
        dialog_posy = dialog_posy - (extra_height / 2)
        button_posy = button_posy - (extra_height / 2)
        self.getControl(999).setPosition(dialog_posx, dialog_posy)
        self.getControl(999).setHeight(dialog_height)
        for button in range(len(self.labels)):
            self.getControl(button + 1001).setPosition(button_posx, button_posy + (button_height * button))
            self.getControl(button + 1001).setLabel(self.labels[button])
            self.getControl(button + 1001).setVisible(True)
            self.getControl(button + 1001).setEnabled(True)

    def _close_dialog(self, selection=None):
        self.selection = selection
        self.close()

    def onClick(self, controlId):
        self._close_dialog(controlId - 1001)

    def onFocus(self, controlId):
        pass
