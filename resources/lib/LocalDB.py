# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import json
import itertools
import KodiJson
import Utils
import addon
import time

PLUGIN_BASE = "plugin://script.extendedinfo/?info="


class LocalDB(object):

    def __init__(self, *args, **kwargs):
        self.info = {}
        self.artists = []
        self.albums = []

    def get_artists(self):
        self.artists = KodiJson.get_artists(properties=["musicbrainzartistid", "thumbnail"])
        return self.artists

    def get_similar_artists(self, artist_id):
        import LastFM
        simi_artists = LastFM.get_similar_artists(artist_id)
        if simi_artists is None:
            Utils.log('Last.fm didn\'t return proper response')
            return None
        if not self.artists:
            self.artists = self.get_artists()
        artists = []
        for simi_artist, kodi_artist in itertools.product(simi_artists, self.artists):
            if kodi_artist['musicbrainzartistid'] and kodi_artist['musicbrainzartistid'] == simi_artist['mbid']:
                artists.append(kodi_artist)
            elif kodi_artist['artist'] == simi_artist['name']:
                data = Utils.get_kodi_json(method="AudioLibrary.GetArtistDetails",
                                           params='{"properties": ["genre", "description", "mood", "style", "born", "died", "formed", "disbanded", "yearsactive", "instrument", "fanart", "thumbnail"], "artistid": %s}' % str(kodi_artist['artistid']))
                item = data["result"]["artistdetails"]
                artwork = {"thumb": item['thumbnail'],
                           "fanart": item['fanart']}
                artists.append({"label": item['label'],
                                "artwork": artwork,
                                "title": item['label'],
                                "Genre": " / ".join(item['genre']),
                                "Artist_Description": item['description'],
                                "userrating": item['userrating'],
                                "Born": item['born'],
                                "Died": item['died'],
                                "Formed": item['formed'],
                                "Disbanded": item['disbanded'],
                                "YearsActive": " / ".join(item['yearsactive']),
                                "Style": " / ".join(item['style']),
                                "Mood": " / ".join(item['mood']),
                                "Instrument": " / ".join(item['instrument']),
                                "LibraryPath": 'musicdb://artists/%s/' % item['artistid']})
        Utils.log('%i of %i artists found in last.FM are in Kodi database' % (len(artists), len(simi_artists)))
        return artists

    def get_similar_movies(self, dbid):
        movie = Utils.get_kodi_json(method="VideoLibrary.GetMovieDetails",
                                    params='{"properties": ["genre","director","country","year","mpaa"], "movieid":%s }' % dbid)
        if "moviedetails" not in movie['result']:
            return []
        comp_movie = movie['result']['moviedetails']
        genres = comp_movie['genre']
        data = Utils.get_kodi_json(method="VideoLibrary.GetMovies",
                                   params='{"properties": ["genre","director","mpaa","country","year"], "sort": { "method": "random" } }')
        if "movies" not in data['result']:
            return []
        quotalist = []
        for item in data['result']['movies']:
            item["mediatype"] = "movie"
            diff = abs(int(item['year']) - int(comp_movie['year']))
            hit = 0.0
            miss = 0.00001
            quota = 0.0
            for genre in genres:
                if genre in item['genre']:
                    hit += 1.0
                else:
                    miss += 1.0
            if hit > 0.0:
                quota = float(hit) / float(hit + miss)
            if genres and item['genre'] and genres[0] == item['genre'][0]:
                quota += 0.3
            if diff < 3:
                quota += 0.3
            elif diff < 6:
                quota += 0.15
            if comp_movie['country'] and item['country'] and comp_movie['country'][0] == item['country'][0]:
                quota += 0.4
            if comp_movie['mpaa'] and item['mpaa'] and comp_movie['mpaa'] == item['mpaa']:
                quota += 0.4
            if comp_movie['director'] and item['director'] and comp_movie['director'][0] == item['director'][0]:
                quota += 0.6
            quotalist.append((quota, item["movieid"]))
        quotalist = sorted(quotalist,
                           key=lambda quota: quota[0],
                           reverse=True)
        movies = []
        for i, list_movie in enumerate(quotalist):
            if comp_movie['movieid'] is not list_movie[1]:
                newmovie = self.get_movie(list_movie[1])
                movies.append(newmovie)
                if i == 20:
                    break
        return movies

    def get_movies(self, filter_str="", limit=10):
        props = '"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director", "writer", "cast", "dateadded", "imdbnumber"]'
        data = Utils.get_kodi_json(method="VideoLibrary.GetMovies",
                                   params='{%s, %s, "limits": {"end": %d}}' % (props, filter_str, limit))
        if "result" in data and "movies" in data["result"]:
            return [self.handle_movies(item) for item in data["result"]["movies"]]
        else:
            return []

    def get_tvshows(self, filter_str="", limit=10):
        props = '"properties": ["title", "genre", "year", "rating", "plot", "studio", "mpaa", "cast", "playcount", "episode", "imdbnumber", "premiered", "votes", "lastplayed", "fanart", "thumbnail", "file", "originaltitle", "sorttitle", "episodeguide", "season", "watchedepisodes", "dateadded", "tag", "art"]'
        data = Utils.get_kodi_json(method="VideoLibrary.GetTVShows",
                                   params='{%s, %s, "limits": {"end": %d}}' % (props, filter_str, limit))
        if "result" in data and "tvshows" in data["result"]:
            return [self.handle_tvshows(item) for item in data["result"]["tvshows"]]
        else:
            return []

    def handle_movies(self, movie):
        trailer = PLUGIN_BASE + "playtrailer&&dbid=%s" % str(movie['movieid'])
        if addon.setting("infodialog_onclick") != "false":
            path = PLUGIN_BASE + 'extendedinfo&&dbid=%s' % str(movie['movieid'])
        else:
            path = PLUGIN_BASE + 'playmovie&&dbid=%i' % movie['movieid']
        if (movie['resume']['position'] and movie['resume']['total']) > 0:
            resume = "true"
            played = '%s' % int((float(movie['resume']['position']) / float(movie['resume']['total'])) * 100)
        else:
            resume = "false"
            played = '0'
        stream_info = Utils.media_streamdetails(movie['file'].encode('utf-8').lower(),
                                                movie['streamdetails'])
        db_movie = Utils.ListItem(label=movie.get('label'),
                                  path=path)
        db_movie.set_infos({'title': movie.get('label'),
                            'File': movie.get('file'),
                            'year': str(movie.get('year')),
                            'writer': " / ".join(movie['writer']),
                            'userrating': movie.get('userrating'),
                            'trailer': trailer,
                            'Rating': str(round(float(movie['rating']), 1)),
                            'director': " / ".join(movie.get('director')),
                            'writer': " / ".join(movie.get('writer')),
                            'plot': movie.get('plot'),
                            'originaltitle': movie.get('originaltitle')})
        db_movie.set_properties({'imdb_id': movie.get('imdbnumber'),
                                 'PercentPlayed': played,
                                 'Resume': resume,
                                 'dbid': str(movie['movieid'])})
        db_movie.set_artwork(movie['art'])
        streams = []
        for i, item in enumerate(movie['streamdetails']['audio'], start=1):
            language = item['language']
            if language not in streams and language != "und":
                streams.append(language)
                streaminfo = {'AudioLanguage.%d' % i: language,
                              'AudioCodec.%d' % i: item["codec"],
                              'AudioChannels.%d' % i: str(item['channels'])}
                db_movie.update_properties(streaminfo)
        subs = []
        for i, item in enumerate(movie['streamdetails']['subtitle'], start=1):
            language = item['language']
            if language not in subs and language != "und":
                subs.append(language)
                db_movie["properties"]['SubtitleLanguage.%d' % i] = language
        db_movie["properties"].update(stream_info)
        return {k: v for k, v in db_movie.items() if v}

    def handle_tvshows(self, tvshow):
        if addon.setting("infodialog_onclick") != "false":
            path = PLUGIN_BASE + 'extendedtvinfo&&dbid=%s' % tvshow['tvshowid']
        else:
            path = PLUGIN_BASE + 'action&&id=ActivateWindow(videos,videodb://tvshows/titles/%s/,return)' % tvshow['tvshowid']
        db_tvshow = Utils.ListItem(label=tvshow.get("label"),
                                   path=path)
        db_tvshow.set_infos({'title': tvshow.get('label'),
                             'genre': " / ".join(tvshow.get('genre')),
                             'Rating': str(round(float(tvshow['rating']), 1)),
                             'year': str(tvshow.get('year')),
                             'originaltitle': tvshow.get('originaltitle')})
        db_tvshow.set_properties({'imdb_id': tvshow.get('imdbnumber'),
                                  'Play': "",
                                  'File': tvshow.get('file'),
                                  'dbid': tvshow['tvshowid']})
        db_tvshow.set_artwork(tvshow['art'])
        return {k: v for k, v in db_tvshow.items() if v}

    def get_movie(self, movie_id):
        response = Utils.get_kodi_json(method="VideoLibrary.GetMovieDetails",
                                       params='{"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director", "writer", "cast", "dateadded", "imdbnumber"], "movieid":%s }' % str(movie_id))
        if "result" in response and "moviedetails" in response["result"]:
            return self.handle_movies(response["result"]["moviedetails"])
        return {}

    def get_tvshow(self, tvshow_id):
        response = Utils.get_kodi_json(method="VideoLibrary.GetTVShowDetails",
                                       params='{"properties": ["title", "genre", "year", "rating", "plot", "studio", "mpaa", "cast", "playcount", "episode", "imdbnumber", "premiered", "votes", "lastplayed", "fanart", "thumbnail", "file", "originaltitle", "sorttitle", "episodeguide", "season", "watchedepisodes", "dateadded", "tag", "art"], "tvshowid":%s }' % str(tvshow_id))
        if "result" in response and "tvshowdetails" in response["result"]:
            return self.handle_tvshows(response["result"]["tvshowdetails"])
        return {}

    def get_albums(self):
        data = Utils.get_kodi_json(method="AudioLibrary.GetAlbums",
                                   params='{"properties": ["title"]}')
        if "result" not in data or "albums" not in data['result']:
            return []
        return data['result']['albums']

    def get_compare_info(self, media_type="movie", items=None):
        """
        fetches info needed for the locally-available check
        Caches some info as window properties.
        Hacky, but by far fastest way to cache between sessions
        """
        infos = ["ids", "imdbs", "otitles", "titles"]
        if not self.info.get(media_type):
            self.info[media_type] = {}
            dct = self.info[media_type]
            # now = time.time()
            dct["ids"] = addon.get_global("%s_ids.JSON" % media_type)
            if dct["ids"] and dct["ids"] != "[]":
                dct["ids"] = json.loads(dct["ids"])
                dct["otitles"] = json.loads(addon.get_global("%s_otitles.JSON" % media_type))
                dct["titles"] = json.loads(addon.get_global("%s_titles.JSON" % media_type))
                dct["imdbs"] = json.loads(addon.get_global("%s_imdbs.JSON" % media_type))
            else:
                for info in infos:
                    dct[info] = []
                for item in items:
                    dct["ids"].append(item["%sid" % media_type])
                    dct["imdbs"].append(item["imdbnumber"])
                    dct["otitles"].append(item["originaltitle"].lower())
                    dct["titles"].append(item["label"].lower())
                for info in infos:
                    addon.set_global("%s_%s.JSON" % (media_type, info), json.dumps(dct[info]))

            self.info[media_type] = dct

    def merge_with_local(self, media_type, items, library_first=True, sortkey=False):
        get_list = KodiJson.get_movies if media_type == "movie" else KodiJson.get_tvshows
        self.get_compare_info(media_type,
                              get_list(["originaltitle", "imdbnumber"]))
        local_items = []
        remote_items = []
        info = self.info[media_type]
        for item in items:
            index = False
            imdb_id = item["properties"].get("imdb_id")
            title = item["infos"]['title'].lower()
            otitle = item["infos"]["originaltitle"].lower()
            if "imdb_id" in item.get("properties", {}) and imdb_id in info["imdbs"]:
                index = info["imdbs"].index(imdb_id)
            elif "title" in item.get("infos", {}) and title in info["titles"]:
                index = info["titles"].index(title)
            elif "originaltitle" in item.get("infos", {}) and otitle in info["otitles"]:
                index = info["otitles"].index(otitle)
            if index:
                get_info = self.get_movie if media_type == "movie" else self.get_tvshow
                local_item = get_info(info["ids"][index])
                if local_item:
                    try:
                        diff = abs(int(local_item["year"]) - int(item["infos"]["year"]))
                        if diff > 1:
                            remote_items.append(item)
                            continue
                    except Exception:
                        pass
                    item["properties"].update(local_item["properties"])
                    item["infos"].update(local_item["infos"])
                    item["artwork"].update(local_item["artwork"])
                    if library_first:
                        local_items.append(item)
                    else:
                        remote_items.append(item)
                else:
                    remote_items.append(item)
            else:
                remote_items.append(item)
        if sortkey:
            local_items = sorted(local_items,
                                 key=lambda k: k["infos"][sortkey],
                                 reverse=True)
            remote_items = sorted(remote_items,
                                  key=lambda k: k["infos"][sortkey],
                                  reverse=True)
        return local_items + remote_items

    def compare_album_with_library(self, online_list):
        if not self.albums:
            self.albums = self.get_albums()
        for item in online_list:
            for local_item in self.albums:
                if not item["name"] == local_item["title"]:
                    continue
                data = Utils.get_kodi_json(method="AudioLibrary.getAlbumDetails",
                                           params='{"properties": ["thumbnail"], "albumid":%s }' % local_item["albumid"])
                album = data["result"]["albumdetails"]
                item["dbid"] = album["albumid"]
                item["path"] = PLUGIN_BASE + 'playalbum&&dbid=%i' % album['albumid']
                if album["thumbnail"]:
                    item.update({"thumb": album["thumbnail"]})
                break
        return online_list

    def get_set_name(self, dbid):
        data = Utils.get_kodi_json(method="VideoLibrary.GetMovieDetails",
                                   params='{"properties": ["setid"], "movieid":%s }' % dbid)
        if "result" not in data or "moviedetails" not in data["result"]:
            return None
        set_dbid = data['result']['moviedetails'].get('setid')
        if set_dbid:
            data = Utils.get_kodi_json(method="VideoLibrary.GetMovieSetDetails",
                                       params='{"setid":%s }' % set_dbid)
            return data['result']['setdetails'].get('label')

    def get_imdb_id(self, media_type, dbid):
        if not dbid:
            return None
        if media_type == "movie":
            data = Utils.get_kodi_json(method="VideoLibrary.GetMovieDetails",
                                       params='{"properties": ["imdbnumber","title", "year"], "movieid":%s }' % dbid)
            if "result" in data and "moviedetails" in data["result"]:
                return data['result']['moviedetails']['imdbnumber']
        elif media_type == "tvshow":
            data = Utils.get_kodi_json(method="VideoLibrary.GetTVShowDetails",
                                       params='{"properties": ["imdbnumber","title", "year"], "tvshowid":%s }' % dbid)
            if "result" in data and "tvshowdetails" in data["result"]:
                return data['result']['tvshowdetails']['imdbnumber']
        return None

    def get_tvshow_id_by_episode(self, dbid):
        if not dbid:
            return None
        data = Utils.get_kodi_json(method="VideoLibrary.GetEpisodeDetails",
                                   params='{"properties": ["tvshowid"], "episodeid":%s }' % dbid)
        if "episodedetails" not in data["result"]:
            return None
        return self.get_imdb_id(media_type="tvshow",
                                dbid=str(data['result']['episodedetails']['tvshowid']))

local_db = LocalDB()
