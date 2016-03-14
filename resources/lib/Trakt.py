# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import datetime
from Utils import *
from LocalDB import local_db

TRAKT_KEY = 'e9a7fba3fa1b527c08c073770869c258804124c5d7c984ce77206e695fbaddd5'
BASE_URL = "https://api-v2launch.trakt.tv/"
HEADERS = {
    'Content-Type': 'application/json',
    'trakt-api-key': TRAKT_KEY,
    'trakt-api-version': 2
}
PLUGIN_BASE = "plugin://script.extendedinfo/?info="


def get_calendar_shows(content):
    shows = []
    url = ""
    if content == "shows":
        url = 'calendars/shows/%s/14' % datetime.date.today()
    elif content == "premieres":
        url = 'calendars/shows/premieres/%s/14' % datetime.date.today()
    results = get_data(url=url,
                       params={"extended": "full,images"},
                       cache_days=0.3)
    count = 1
    if not results:
        return None
    for day in results.iteritems():
        for episode in day[1]:
            title = episode["episode"]["title"] if episode["episode"]["title"] else ""
            show = {'label': u"{0} - {1}x{2}. {3}".format(episode["show"]["title"],
                                                          episode["episode"]["season"],
                                                          episode["episode"]["number"],
                                                          title),
                    'path': PLUGIN_BASE + 'extendedtvinfo&&tvdb_id=%s' % episode["show"]["ids"]["tvdb"],
                    'title': title,
                    'season': episode["episode"]["season"],
                    'episode': episode["episode"]["number"],
                    'TVShowTitle': episode["show"]["title"],
                    'mediatype': "episode",
                    'year': fetch(episode["show"], "year"),
                    'duration': episode["show"]["runtime"],
                    'Studio': episode["show"]["network"],
                    'Plot': episode["show"]["overview"],
                    'genre': " / ".join(episode["show"]["genres"]),
                    'mpaa': episode["show"]["certification"]}
            show["properties"] = {'tvdb_id': episode["show"]["ids"]["tvdb"],
                                  'id': episode["show"]["ids"]["tvdb"],
                                  'imdb_id': episode["show"]["ids"]["imdb"],
                                  'duration(h)': format_time(episode["show"]["runtime"], "h"),
                                  'duration(m)': format_time(episode["show"]["runtime"], "m")}
            show["artwork"] = {'thumb': episode["episode"]["images"]["screenshot"]["thumb"],
                               'poster': episode["show"]["images"]["poster"]["full"],
                               'Banner': episode["show"]["images"]["banner"]["full"],
                               'fanart': episode["show"]["images"]["fanart"]["full"]}
            shows.append(show)
            count += 1
            if count > 20:
                break
    return shows


def handle_movies(results):
    movies = []
    path = 'extendedinfo&&id=%s' if SETTING("infodialog_onclick") != "false" else "playtrailer&&id=%s"
    for item in results:
        movie = {'label': item["movie"]["title"],
                 'path': PLUGIN_BASE + path % fetch(item["movie"]["ids"], 'tmdb'),
                 'title': item["movie"]["title"],
                 'duration': item["movie"]["runtime"],
                 'Tagline': item["movie"]["tagline"],
                 'mediatype': "movie",
                 'Trailer': convert_youtube_url(item["movie"]["trailer"]),
                 'year': item["movie"]["year"],
                 'mpaa': item["movie"]["certification"],
                 'Plot': item["movie"]["overview"],
                 'Premiered': item["movie"]["released"],
                 'Rating': round(item["movie"]["rating"], 1),
                 'Votes': item["movie"]["votes"],
                 'genre': " / ".join(item["movie"]["genres"])}
        movie["properties"] = {'id': item["movie"]["ids"]["tmdb"],
                               'imdb_id': item["movie"]["ids"]["imdb"],
                               'Watchers': item["watchers"],
                               'duration(h)': format_time(item["movie"]["runtime"], "h"),
                               'duration(m)': format_time(item["movie"]["runtime"], "m")}
        movie["artwork"] = {'poster': item["movie"]["images"]["poster"]["full"],
                            'fanart': item["movie"]["images"]["fanart"]["full"],
                            'thumb': item["movie"]["images"]["poster"]["thumb"]}
        movies.append(movie)
    movies = local_db.merge_with_local_movie_info(online_list=movies,
                                                  library_first=False)
    return movies


def handle_tvshows(results):
    shows = []
    for tvshow in results:
        airs = fetch(tvshow['show'], "airs")
        path = PLUGIN_BASE + 'extendedtvinfo&&tvdb_id=%s' % tvshow['show']['ids']["tvdb"]
        show = {'title': tvshow['show']["title"],
                'label': tvshow['show']["title"],
                'mediatype': "tvshow",
                'path': path,
                'TVShowTitle': tvshow['show']["title"],
                'duration': tvshow['show']["runtime"],
                'year': tvshow['show']["year"],
                'Premiered': tvshow['show']["first_aired"][:10],
                'Country': tvshow['show']["country"],
                'Rating': round(tvshow['show']["rating"], 1),
                'Votes': tvshow['show']["votes"],
                'mpaa': tvshow['show']["certification"],
                'Studio': tvshow['show']["network"],
                'genre': " / ".join(tvshow['show']["genres"]),
                'Plot': tvshow['show']["overview"]}
        show["properties"] = {'id': tvshow['show']['ids']["tmdb"],
                              'tvdb_id': tvshow['show']['ids']["tvdb"],
                              'imdb_id': tvshow['show']['ids']["imdb"],
                              'duration(h)': format_time(tvshow['show']["runtime"], "h"),
                              'duration(m)': format_time(tvshow['show']["runtime"], "m"),
                              'Status': fetch(tvshow['show'], "status"),
                              'AirDay': fetch(airs, "day"),
                              'AirShortTime': fetch(airs, "time"),
                              'Watchers': fetch(tvshow, "watchers")}
        show["artwork"] = {'poster': tvshow['show']["images"]["poster"]["full"],
                           'Banner': tvshow['show']["images"]["banner"]["full"],
                           'fanart': tvshow['show']["images"]["fanart"]["full"],
                           'thumb': tvshow['show']["images"]["poster"]["thumb"]}
        shows.append(show)
    shows = local_db.merge_with_local_tvshow_info(online_list=shows,
                                                  library_first=False)
    return shows


def get_trending_shows():
    results = get_data(url='shows/trending',
                       params={"extended": "full,images"})
    if not results:
        return []
    return handle_tvshows(results)


def get_tshow_info(imdb_id):
    results = get_data(url='show/%s' % imdb_id,
                       params={"extended": "full,images"})
    if not results:
        return []
    return handle_tvshows([results])


def get_trending_movies():
    results = get_data(url='movies/trending',
                       params={"extended": "full,images"})
    if not results:
        return []
    return handle_movies(results)


def get_similar(media_type, imdb_id):
    if not imdb_id or not media_type:
        return None
    results = get_data(url='%s/%s/related' % (media_type, imdb_id),
                       params={"extended": "full,images"})
    if not results:
        return None
    if media_type == "show":
        return handle_tvshows(results)
    elif media_type == "movie":
        return handle_movies(results)


def get_data(url, params={}, cache_days=10):
    url = "%s%s?%s" % (BASE_URL, url, urllib.urlencode(params))
    return get_JSON_response(url=url,
                             folder="Trakt",
                             headers=HEADERS,
                             cache_days=cache_days)
