# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import Utils


def play_media(media_type, dbid, resume=True):
    if media_type in ['movie', 'episode']:
        Utils.get_kodi_json(method="Player.Open",
                            params='{"item": {"%sid": %s}, "options":{"resume": %s}}' % (media_type, dbid, str(resume).lower()))
    elif media_type in ['musicvideo', 'album', 'song']:
        Utils.get_kodi_json(method="Player.Open",
                            params='{"item": {"%sid": %s}}' % (media_type, dbid))


def send_text(text, close_keyboard=True):
    Utils.get_kodi_json(method="Input.SendText",
                        params='{"text":"%s", "done":%s}' % (text, "true" if close_keyboard else "false"))


def get_artists(properties=None):
    properties = [] if not properties else properties
    data = Utils.get_kodi_json(method="AudioLibrary.GetArtists",
                               params='{"properties": ["%s"]}' % '","'.join(properties))
    if "result" in data and "artists" in data["result"]:
        return data["result"]["artists"]
    return []


def get_movies(properties=None):
    properties = [] if not properties else properties
    data = Utils.get_kodi_json(method="VideoLibrary.GetMovies",
                               params='{"properties": ["%s"]}' % '","'.join(properties))
    if "result" in data and "movies" in data["result"]:
        return data["result"]["movies"]
    return []


def get_tvshows(properties=None):
    properties = [] if not properties else properties
    data = Utils.get_kodi_json(method="VideoLibrary.GetTVShows",
                               params='{"properties": ["%s"]}' % '","'.join(properties))
    if "result" in data and "tvshows" in data["result"]:
        return data["result"]["tvshows"]
    return []
