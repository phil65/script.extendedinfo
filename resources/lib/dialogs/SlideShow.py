# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from resources.lib import Utils

import windows


class SlideShow(windows.DialogXML):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    ID_LIST_PICTURES = 5000

    def __init__(self, *args, **kwargs):
        self.images = kwargs.get('listitems')
        self.index = kwargs.get('index')
        self.image = kwargs.get('image')
        self.action = None

    def onInit(self):
        super(SlideShow, self).onInit()
        if not self.images:
            return None
        self.getControl(self.ID_LIST_PICTURES).addItems(Utils.create_listitems(self.images))
        self.getControl(self.ID_LIST_PICTURES).selectItem(self.index)
        self.setFocusId(self.ID_LIST_PICTURES)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.position = self.getControl(self.ID_LIST_PICTURES).getSelectedPosition()
            self.close()
