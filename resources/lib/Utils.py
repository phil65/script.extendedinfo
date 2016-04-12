# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
import re
import threading

from kodi65 import utils


def dictfind(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return dic
    return ""


def fetch_musicbrainz_id(artist, artist_id=-1):
    """
    fetches MusicBrainz ID for given *artist and returns it
    uses musicbrainz.org
    """
    base_url = "http://musicbrainz.org/ws/2/artist/?fmt=json"
    url = '&query=artist:%s' % urllib.quote_plus(artist)
    results = utils.get_JSON_response(url=base_url + url,
                                      cache_days=30,
                                      folder="MusicBrainz")
    if results and len(results["artists"]) > 0:
        utils.log("found artist id for %s: %s" % (artist, results["artists"][0]["id"]))
        return results["artists"][0]["id"]
    else:
        return None


class FunctionThread(threading.Thread):

    def __init__(self, function=None, param=None):
        threading.Thread.__init__(self)
        self.function = function
        self.param = param
        self.setName(self.function.__name__)
        utils.log("init " + self.function.__name__)

    def run(self):
        self.listitems = self.function(self.param)
        return True


def convert_youtube_url(raw_string):
    """
    get plugin playback URL for URL *raw_string
    """
    youtube_id = extract_youtube_id(raw_string)
    if youtube_id:
        return 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % youtube_id
    return ""


def extract_youtube_id(raw_string):
    """
    get youtube video id if from youtube URL
    """
    vid_ids = None
    if raw_string and 'youtube.com/v' in raw_string:
        vid_ids = re.findall('http://www.youtube.com/v/(.{11})\??', raw_string, re.DOTALL)
    elif raw_string and 'youtube.com/watch' in raw_string:
        vid_ids = re.findall('youtube.com/watch\?v=(.{11})\??', raw_string, re.DOTALL)
    if vid_ids:
        return vid_ids[0]
    else:
        return ""


def reduce_list(items, key="job"):
    """
    TODO: refactor
    """
    crew_ids = []
    crews = []
    for item in items:
        id_ = item.get_property("id")
        if id_ not in crew_ids:
            crew_ids.append(id_)
            crews.append(item)
        else:
            index = crew_ids.index(id_)
            if key in crews[index]:
                crews[index][key] = crews[index][key] + " / " + item[key]
    return crews
