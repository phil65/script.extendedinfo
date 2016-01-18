# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
from Utils import *

# TVRAGE_KEY = 'VBp9BuIr5iOiBeWCFRMG'
BANDSINTOWN_KEY = 'xbmc_open_source_media_center'
BASE_URL = "http://api.bandsintown.com/events/search?format=json&api_version=2.0&"


def handle_events(results):
    events = []
    for event in results:
        venue = event['venue']
        artists = ''
        for art in event["artists"]:
            artists = artists + ' / ' + art['name']
            artists = artists.replace(" / ", "", 1)
        events.append({'date': event['datetime'].replace("T", " - ").replace(":00", "", 1),
                       'city': venue['city'],
                       'lat': venue['latitude'],
                       'lon': venue['longitude'],
                       'id': venue['id'],
                       'url': venue['url'],
                       'name': venue['name'],
                       'region': venue['region'],
                       'country': venue['country'],
                       'artists': artists})
    return events


def get_near_events(artists):  # not possible with api 2.0
    artist_str = ''
    for count, art in enumerate(artists[:50]):
        try:
            artist = urllib.quote(art['artist'])
        except:
            artist = urllib.quote(art['artist'].encode("utf-8"))
        if len(artist_str) > 0:
            artist_str = artist_str + '&'
        artist_str = artist_str + 'artists[]=' + artist
    url = BASE_URL + 'location=use_geoip&radius=50&per_page=100&%sapp_id=%s' % (artist_str, BANDSINTOWN_KEY)
    results = get_JSON_response(url, folder="BandsInTown")
    if results:
        return handle_events(results)
    log("get_near_events: Could not get data from " + url)
    log(results)
    return []
