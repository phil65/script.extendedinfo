# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
import re
import threading

from kodi65 import utils


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
