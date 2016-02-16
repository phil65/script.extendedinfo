# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import random
import xbmc
from Utils import *
import datetime

# TVRAGE_KEY = 'VBp9BuIr5iOiBeWCFRMG'

def get_babe_images(single=False):
    now = datetime.datetime.now()
    filename = "babe%ix%ix%i" % (now.month, now.day, now.year)
    if single:
        filename= "single" + filename
    path = xbmc.translatePath(os.path.join(ADDON_DATA_PATH, "Babes", filename + ".txt"))
    if xbmcvfs.exists(path):
        return read_from_file(path)
    items = []
    for i in range(1, 10):
        if single:
            month = now.month
            day = now.day
            image = i
        else:
            month = random.randrange(1, 9)
            day = random.randrange(1, 28)
            image = random.randrange(1, 8)
        url = 'http://img1.demo.jsxbabeotd.dellsports.com/static/models/2014/%s/%s/%i.jpg' % (str(month).zfill(2), str(day).zfill(2), image)
        newitem = {'thumb': url,
                   'path': "plugin://script.extendedinfo?info=setfocus",
                   'title': "2014/%i/%i (Nr. %i)" % (month, day, image)
                   }
        items.append(newitem)
    save_to_file(content=items,
                 filename=filename,
                 path=os.path.join(ADDON_DATA_PATH, "Babes"))
    return items
