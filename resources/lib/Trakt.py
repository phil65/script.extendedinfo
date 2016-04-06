# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import datetime
import Utils
import addon
from LocalDB import local_db
import urllib

TRAKT_KEY = 'e9a7fba3fa1b527c08c073770869c258804124c5d7c984ce77206e695fbaddd5'
BASE_URL = "https://api-v2launch.trakt.tv/"
HEADERS = {
    'Content-Type': 'application/json',
    'trakt-api-key': TRAKT_KEY,
    'trakt-api-version': 2
}
PLUGIN_BASE = "plugin://script.extendedinfo/?info="


def get_episodes(content):
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
            label = u"{0} - {1}x{2}. {3}".format(episode["show"]["title"],
                                                 episode["episode"]["season"],
                                                 episode["episode"]["number"],
                                                 title)
            show = Utils.ListItem(label=label,
                                  path=PLUGIN_BASE + 'extendedtvinfo&&tvdb_id=%s' % episode["show"]["ids"]["tvdb"])
            show.set_infos({'title': title,
                            'premiered': episode["episode"]["first_aired"],
                            'season': episode["episode"]["season"],
                            'episode': episode["episode"]["number"],
                            'tvshowtitle': episode["show"]["title"],
                            'mediatype': "episode",
                            'year': episode["show"].get("year"),
                            'duration': episode["show"]["runtime"] * 60,
                            'studio': episode["show"]["network"],
                            'plot': episode["show"]["overview"],
                            'country': episode["show"]["country"],
                            'status': episode["show"]["status"],
                            'trailer': episode["show"]["trailer"],
                            'rating': episode["show"]["rating"],
                            'genre': " / ".join(episode["show"]["genres"]),
                            'mpaa': episode["show"]["certification"]})
            show.set_properties({'tvdb_id': episode["episode"]["ids"]["tvdb"],
                                 'id': episode["episode"]["ids"]["tvdb"],
                                 'imdb_id': episode["episode"]["ids"]["imdb"],
                                 'homepage': episode["show"]["homepage"],
                                 'duration(h)': Utils.format_time(episode["show"]["runtime"], "h"),
                                 'duration(m)': Utils.format_time(episode["show"]["runtime"], "m")})
            show.set_artwork({'thumb': episode["episode"]["images"]["screenshot"]["thumb"],
                              'poster': episode["show"]["images"]["poster"]["full"],
                              'banner': episode["show"]["images"]["banner"]["full"],
                              'clearart': episode["show"]["images"]["clearart"]["full"],
                              'clearlogo': episode["show"]["images"]["logo"]["full"],
                              'fanart': episode["show"]["images"]["fanart"]["full"]})
            shows.append(show)
            count += 1
            if count > 20:
                break
    return shows


def handle_movies(results):
    movies = []
    path = 'extendedinfo&&id=%s' if addon.bool_setting("infodialog_onclick") else "playtrailer&&id=%s"
    for item in results:
        if "movie" in item:
            item = item["movie"]
        movie = Utils.ListItem(label=item["title"],
                               path=PLUGIN_BASE + path % item["ids"]["tmdb"])
        movie.set_infos({'title': item["title"],
                         'duration': item["runtime"] * 60,
                         'tagline': item["tagline"],
                         'mediatype': "movie",
                         'trailer': Utils.convert_youtube_url(item["trailer"]),
                         'year': item["year"],
                         'mpaa': item["certification"],
                         'plot': item["overview"],
                         'premiered': item["released"],
                         'rating': round(item["rating"], 1),
                         'votes': item["votes"],
                         'genre': " / ".join(item["genres"])})
        movie.set_properties({'id': item["ids"]["tmdb"],
                              'imdb_id': item["ids"]["imdb"],
                              'watchers': item.get("watchers"),
                              'duration(h)': Utils.format_time(item["runtime"], "h"),
                              'duration(m)': Utils.format_time(item["runtime"], "m")})
        movie.set_artwork({'poster': item["images"]["poster"]["full"],
                           'fanart': item["images"]["fanart"]["full"],
                           'clearlogo': item["images"]["logo"]["full"],
                           'clearart': item["images"]["clearart"]["full"],
                           'banner': item["images"]["banner"]["full"],
                           'thumb': item["images"]["poster"]["thumb"]})
        movies.append(movie)
    movies = local_db.merge_with_local(media_type="movie",
                                       online_list=movies,
                                       library_first=False)
    return movies


def handle_tvshows(results):
    shows = []
    for item in results:
        airs = item['show'].get("airs", {})
        show = Utils.ListItem(label=item['show']["title"],
                              path='%sextendedtvinfo&&tvdb_id=%s' % (PLUGIN_BASE, item['show']['ids']["tvdb"]))
        show.set_infos({'mediatype': "tvshow",
                        'title': item['show']["title"],
                        'tvshowtitle': item['show']["title"],
                        'duration': item['show']["runtime"] * 60,
                        'year': item['show']["year"],
                        'premiered': item['show']["first_aired"][:10],
                        'country': item['show']["country"],
                        'rating': round(item['show']["rating"], 1),
                        'votes': item['show']["votes"],
                        'mpaa': item['show']["certification"],
                        'trailer': item["show"]["trailer"],
                        'status': item['show'].get("status"),
                        'studio': item['show']["network"],
                        'genre': " / ".join(item['show']["genres"]),
                        'plot': item['show']["overview"]})
        show.set_properties({'id': item['show']['ids']["tmdb"],
                             'tvdb_id': item['show']['ids']["tvdb"],
                             'imdb_id': item['show']['ids']["imdb"],
                             'duration(h)': Utils.format_time(item['show']["runtime"], "h"),
                             'duration(m)': Utils.format_time(item['show']["runtime"], "m"),
                             'homepage': item["show"]["homepage"],
                             'airday': airs.get("day"),
                             'airshorttime': airs.get("time"),
                             'watchers': item.get("watchers")})
        show.set_artwork({'poster': item['show']["images"]["poster"]["full"],
                          'banner': item['show']["images"]["banner"]["full"],
                          'clearart': item['show']["images"]["clearart"]["full"],
                          'clearlogo': item['show']["images"]["logo"]["full"],
                          'fanart': item['show']["images"]["fanart"]["full"],
                          'thumb': item['show']["images"]["poster"]["thumb"]})
        shows.append(show)
    shows = local_db.merge_with_local(media_type="tvshow",
                                      online_list=shows,
                                      library_first=False)
    return shows


def get_shows(show_type):
    results = get_data(url='shows/%s' % show_type,
                       params={"extended": "full,images"})
    if not results:
        return []
    return handle_tvshows(results)


def get_shows_from_time(show_type, period="monthly"):
    results = get_data(url='shows/%s/%s' % (show_type, period),
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


def get_movies(movie_type):
    results = get_data(url='movies/%s' % movie_type,
                       params={"extended": "full,images"})
    if not results:
        return []
    return handle_movies(results)


def get_movies_from_time(movie_type, period="monthly"):
    results = get_data(url='movies/%s/%s' % (movie_type, period),
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


def get_data(url, params=None, cache_days=10):
    params = params if params else {}
    params["limit"] = 20
    url = "%s%s?%s" % (BASE_URL, url, urllib.urlencode(params))
    return Utils.get_JSON_response(url=url,
                                   folder="Trakt",
                                   headers=HEADERS,
                                   cache_days=cache_days)
