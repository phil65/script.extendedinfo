# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
import urllib2
import os
import re
import threading

import xbmc
import xbmcvfs

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


def get_file(url):
    clean_url = utils.translate_path(urllib.unquote(url)).replace("image://", "")
    clean_url = clean_url.rstrip("/")
    cached_thumb = xbmc.getCacheThumbName(clean_url)
    vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cached_thumb[0], cached_thumb)
    cache_file_jpg = os.path.join("special://profile/Thumbnails/", cached_thumb[0], cached_thumb[:-4] + ".jpg").replace("\\", "/")
    cache_file_png = cache_file_jpg[:-4] + ".png"
    if xbmcvfs.exists(cache_file_jpg):
        utils.log("cache_file_jpg Image: " + url + "-->" + cache_file_jpg)
        return utils.translate_path(cache_file_jpg)
    elif xbmcvfs.exists(cache_file_png):
        utils.log("cache_file_png Image: " + url + "-->" + cache_file_png)
        return cache_file_png
    elif xbmcvfs.exists(vid_cache_file):
        utils.log("vid_cache_file Image: " + url + "-->" + vid_cache_file)
        return vid_cache_file
    try:
        request = urllib2.Request(clean_url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request, timeout=3)
        data = response.read()
        response.close()
        utils.log('image downloaded: ' + clean_url)
    except Exception:
        utils.log('image download failed: ' + clean_url)
        return ""
    if not data:
        return ""
    image = cache_file_png if url.endswith(".png") else cache_file_jpg
    try:
        with open(utils.translate_path(image), "wb") as f:
            f.write(data)
        return utils.translate_path(image)
    except Exception:
        utils.log('failed to save image ' + url)
        return ""


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
