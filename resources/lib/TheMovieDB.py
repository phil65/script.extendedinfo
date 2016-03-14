# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from Utils import *
from LocalDB import local_db
import re
import urllib2
from functools32 import lru_cache
from WindowManager import wm

TMDB_KEY = '34142515d9d23817496eeb4ff1d223d0'
POSTER_SIZES = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]
LOGO_SIZES = ["w45", "w92", "w154", "w185", "w300", "w500", "original"]
BACKDROP_SIZES = ["w300", "w780", "w1280", "original"]
PROFILE_SIZES = ["w45", "w185", "h632", "original"]
STILL_SIZES = ["w92", "w185", "w300", "original"]
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-agent': 'XBMC/16.0 ( phil65@kodi.tv )'
}
base_url = "http://image.tmdb.org/t/p/"
POSTER_SIZE = "w500"
include_adult = SETTING("include_adults").lower()
if SETTING("use_https"):
    URL_BASE = "https://api.themoviedb.org/3/"
else:
    URL_BASE = "http://api.themoviedb.org/3/"

ALL_MOVIE_PROPS = "account_states,alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating"
ALL_TV_PROPS = "account_states,alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos"
ALL_ACTOR_PROPS = "tv_credits,movie_credits,combined_credits,images,tagged_images"
ALL_SEASON_PROPS = "videos,images,external_ids,credits"
ALL_EPISODE_PROPS = "account_states,credits,external_ids,images,rating,videos"

PLUGIN_BASE = "plugin://script.extendedinfo/?info="

release_types = {1: "Premiere",
                 2: "Theatrical (limited)",
                 3: "Theatrical",
                 4: "Digital",
                 5: "Physical",
                 6: "TV"}


class SettingsMonitor(xbmc.Monitor):

    def __init__(self):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        global Login
        Login = LoginProvider(username=xbmcaddon.Addon().getSetting("tmdb_username"),
                              password=xbmcaddon.Addon().getSetting("tmdb_password"))
        if wm.active_dialog:
            wm.active_dialog.close()
            wm.active_dialog.logged_in = Login.check_login(cache_days=0)
            wm.active_dialog.doModal()


class LoginProvider(object):

    def __init__(self, *args, **kwargs):
        self.session_id = None
        self.request_token = None
        self.account_id = None
        self.monitor = SettingsMonitor()
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")

    def check_login(self, cache_days=9999):
        if self.username:
            return(bool(self.get_session_id(cache_days)))
        return False

    def get_account_id(self):
        '''
        returns TMDB account id
        '''
        if self.account_id:
            return self.account_id
        self.session_id = self.get_session_id()
        response = get_data(url="account",
                            params={"session_id": self.session_id},
                            cache_days=999999)
        if not response:
            return None
        self.account_id = response.get("id")
        return self.account_id

    @lru_cache(maxsize=128)
    def get_guest_session_id(self):
        '''
        returns guest session id for TMDB
        '''
        response = get_data(url="authentication/guest_session/new",
                            cache_days=999999)
        if not response or "guest_session_id" not in response:
            return None
        return str(response["guest_session_id"])

    def get_session_id(self, cache_days=9999):
        '''
        returns session id for TMDB Account
        '''
        if self.session_id:
            return self.session_id
        self.request_token = self.auth_request_token(cache_days=cache_days)
        self.session_id = self.start_new_session(cache_days=cache_days)
        if self.session_id:
            return self.session_id
        self.session_id = self.start_new_session(cache_days=0)
        notify("login failed")
        return None

    def start_new_session(self, cache_days=0):
        response = get_data(url="authentication/session/new",
                            params={"request_token": self.request_token},
                            cache_days=cache_days)
        if response and "success" in response:
            self.session_id = str(response["session_id"])
            return self.session_id

    def auth_request_token(self, cache_days=9999):
        '''
        returns request token, is used to get session_id
        '''
        if self.request_token:
            return self.request_token
        response = get_data(url="authentication/token/new",
                            cache_days=999999)
        self.request_token = response["request_token"]
        params = {"request_token": self.request_token,
                  "username": self.username,
                  "password": self.password}
        response = get_data(url="authentication/token/validate_with_login",
                            params=params,
                            cache_days=cache_days)
        if response and response.get("success"):
            return response["request_token"]


def set_rating_prompt(media_type, media_id, dbid=None):
    if not media_type or not media_id:
        return False
    rating = xbmcgui.Dialog().select(LANG(32129), [str(float(i * 0.5)) for i in range(1, 21)])
    if rating == -1:
        return False
    if dbid:
        if media_type == "movie":
            get_kodi_json(method="VideoLibrary.SetMovieDetails",
                          params='{"movieid":%s,"userrating":%d}' % (dbid, round(rating)))
        elif media_type == "tv":
            get_kodi_json(method="VideoLibrary.SetTVShowDetails",
                          params='{"tvshowid":%s,"userrating":%d}' % (dbid, round(rating)))
        elif media_type == "episode":
            get_kodi_json(method="VideoLibrary.SetEpisodeDetails",
                          params='{"episodeid":%s,"userrating":%d}' % (dbid, round(rating)))
    set_rating(media_type=media_type,
               media_id=media_id,
               rating=(float(rating) * 0.5) + 0.5)
    return True


def set_rating(media_type, media_id, rating):
    '''
    media_type: movie, tv or episode
    media_id: tmdb_id / episode ident array
    rating: ratung value (0.5-10.0, 0.5 steps)
    '''
    params = {}
    if Login.check_login():
        params["session_id"] = Login.get_session_id()
    else:
        params["guest_session_id"] = Login.get_guest_session_id()
    if media_type == "episode":
        if not media_id[1]:
            media_id[1] = "0"
        url = "tv/%s/season/%s/episode/%s/rating" % (media_id[0], media_id[1], media_id[2])
    else:
        url = "%s/%s/rating" % (media_type, media_id)
    # request.get_method = lambda: 'DELETE'
    results = send_request(url=url,
                           params=params,
                           values='{"value": %.1f}' % rating)
    if results:
        notify(ADDON_NAME, results["status_message"])


def send_request(url, params, values, delete=False):
    params["api_key"] = TMDB_KEY
    params = dict((k, v) for (k, v) in params.iteritems() if v)
    params = dict((k, unicode(v).encode('utf-8')) for (k, v) in params.iteritems())
    url = "%s%s?%s" % (URL_BASE, url, urllib.urlencode(params))
    log(url)
    request = urllib2.Request(url=url,
                              data=values,
                              headers=HEADERS)
    if delete:
        request.get_method = lambda: 'DELETE'
    try:
        response = urllib2.urlopen(request, timeout=3).read()
    except urllib2.HTTPError as err:
        if err.code == 401:
            notify("Error", "Not authorized.")
        return None
    return json.loads(response)


def change_fav_status(media_id=None, media_type="movie", status="true"):
    params = {"session_id": Login.get_session_id()}
    values = '{"media_type": "%s", "media_id": %s, "favorite": %s}' % (media_type, media_id, status)
    if not params["session_id"]:
        notify("Could not get session id")
        return None
    results = send_request(url="account/%s/favorite" % Login.get_account_id(),
                           params=params,
                           values=values)
    if results:
        notify(ADDON_NAME, results["status_message"])


def create_list(list_name):
    '''
    creates new list on TMDB with name *list_name
    returns newly created list id
    '''
    values = {'name': '%s' % list_name, 'description': 'List created by ExtendedInfo Script for Kodi.'}
    results = send_request(url="list",
                           params={"session_id": Login.get_session_id()},
                           values=values)
    if results:
        notify(ADDON_NAME, results["status_message"])
    return results["list_id"]


def remove_list(list_id):
    results = send_request(url="list/%s" % list_id,
                           params={"session_id": Login.get_session_id()},
                           values={'media_id': list_id},
                           delete=True)
    if results:
        notify(ADDON_NAME, results["status_message"])
    return results["list_id"]


def change_list_status(list_id, movie_id, status):
    method = "add_item" if status else "remove_item"
    results = send_request(url="list/%s/%s" % (list_id, method),
                           params={"session_id": Login.get_session_id()},
                           values={'media_id': movie_id})
    if results:
        notify(ADDON_NAME, results["status_message"])


def get_account_lists(cache_time=0):
    '''
    returns movie lists for TMDB user
    '''
    session_id = Login.get_session_id()
    account_id = Login.get_account_id()
    if session_id and account_id:
        response = get_data(url="account/%s/lists" % (account_id),
                            params={"session_id": session_id},
                            cache_days=cache_time)
        return response["results"]
    else:
        return []


def get_certification_list(media_type):
    response = get_data(url="certification/%s/list" % media_type,
                        cache_days=999999)
    return response.get("certifications")


def add_movie_to_list(movie_id):
    selection = xbmcgui.Dialog().select(heading=LANG(22080),
                                        list=[LANG(32083)])
    if selection == 0:
        account_lists = get_account_lists()
        listitems = ["%s (%i)" % (i["name"], i["item_count"]) for i in account_lists]
        index = xbmcgui.Dialog().select(LANG(32136), listitems)
        change_list_status(list_id=account_lists[index]["id"],
                           movie_id=movie_id,
                           status=True)


def merge_with_cert_desc(input_list, media_type):
    cert_list = get_certification_list(media_type)
    for item in input_list:
        if item["iso_3166_1"].upper() not in cert_list:
            continue
        hit = dictfind(lst=cert_list[item["iso_3166_1"].upper()],
                       key="certification",
                       value=item["certification"])
        if hit:
            item["meaning"] = hit["meaning"]
    return input_list


def handle_multi_search(results):
    listitems = []
    for item in results:
        if item["mediatype"] == "movie":
            listitems.append(handle_movies([item])[0])
        elif item["mediatype"] == "tvshow":
            listitems.append(handle_tvshows([item])[0])
        else:
            listitems.append(handle_people([item])[0])
    return listitems


def handle_movies(results, local_first=True, sortkey="year"):
    response = get_data(url="genre/movie/list",
                        params={"language": SETTING("LanguageID")},
                        cache_days=30)
    ids = [item["id"] for item in response["genres"]]
    labels = [item["name"] for item in response["genres"]]
    movies = []
    path = 'extendedinfo&&id=%s' if SETTING("infodialog_onclick") != "false" else "playtrailer&&id=%s"
    for movie in results:
        genres = [labels[ids.index(id_)] for id_ in movie.get("genre_ids", []) if id_ in ids]
        trailer = "%splaytrailer&&id=%s" % (PLUGIN_BASE, movie.get("id"))
        item = {'label': movie.get('title'),
                'path': PLUGIN_BASE + path % movie.get("id"),
                'title': movie.get('title'),
                'OriginalTitle': movie.get('original_title', ""),
                'mediatype': "movie",
                'country': movie.get('original_language'),
                'plot': movie.get('overview'),
                'Trailer': trailer,
                'genre': " / ".join([i for i in genres if i]),
                'Votes': movie.get('vote_count'),
                'year': get_year(movie.get('release_date')),
                'Rating': movie.get('vote_average'),
                'Premiered': movie.get('release_date')}
        item["properties"] = {'id': movie.get("id"),
                              'Popularity': movie.get('popularity'),
                              'credit_id': movie.get('credit_id'),
                              'character': movie.get('character'),
                              'job': movie.get('job'),
                              'department': movie.get('department'),
                              'User_Rating': movie.get('rating'),
                              'time_comparer': movie['release_date'].replace("-", "") if movie.get('release_date') else ""}
        item["artwork"] = get_image_urls(poster=movie.get("poster_path"),
                                         fanart=movie.get("backdrop_path"))
        movies.append(item)
    movies = local_db.merge_with_local_movie_info(movies, local_first, sortkey)
    return movies


def handle_tvshows(results, local_first=True, sortkey="year"):
    tvshows = []
    response = get_data(url="genre/tv/list",
                        params={"language": SETTING("LanguageID")},
                        cache_days=30)
    ids = [item["id"] for item in response["genres"]]
    labels = [item["name"] for item in response["genres"]]
    for tv in results:
        tmdb_id = fetch(tv, 'id')
        genres = [labels[ids.index(id_)] for id_ in tv.get("genre_ids", []) if id_ in ids]
        duration = ""
        if "episode_run_time" in tv:
            if len(tv["episode_run_time"]) > 1:
                duration = "%i - %i" % (min(tv["episode_run_time"]), max(tv["episode_run_time"]))
            elif len(tv["episode_run_time"]) == 1:
                duration = "%i" % (tv["episode_run_time"][0])
        newtv = {'title': tv.get('name'),
                 'label': tv.get('name'),
                 'OriginalTitle': tv.get('original_name', ""),
                 'duration': duration,
                 'genre': " / ".join([i for i in genres if i]),
                 'country': tv.get('original_language'),
                 'Plot': tv.get("overview"),
                 'year': get_year(tv.get('first_air_date')),
                 'mediatype': "tvshow",
                 'path': PLUGIN_BASE + 'extendedtvinfo&&id=%s' % tmdb_id,
                 'Rating': tv.get('vote_average'),
                 'Votes': tv.get('vote_count'),
                 'Premiered': tv.get('first_air_date')}
        newtv["properties"] = {'id': tmdb_id,
                               'User_Rating': tv.get('rating'),
                               'character': tv.get('character'),
                               'Popularity': tv.get('popularity'),
                               'credit_id': tv.get('credit_id'),
                               'TotalEpisodes': tv.get('number_of_episodes'),
                               'TotalSeasons': tv.get('number_of_seasons')}
        newtv["artwork"] = get_image_urls(poster=tv.get("poster_path"),
                                          fanart=tv.get("backdrop_path"))
        tvshows.append(newtv)
    tvshows = local_db.merge_with_local_tvshow_info(tvshows, local_first, sortkey)
    return tvshows


def handle_episodes(results):
    listitems = []
    for item in results:
        title = clean_text(item.get("name"))
        if not title:
            title = u"%s %s" % (LANG(20359), item.get('episode_number'))
        listitem = {'mediatype': "episode",
                    'title': title,
                    'label': title,
                    'Premiered': item.get('air_date'),
                    'episode': item.get('episode_number'),
                    'season': item.get('season_number'),
                    'Rating': item.get('vote_average'),
                    'Votes': item.get('vote_count')}
        listitem["properties"] = {'id': item.get('id'),
                                  'production_code': item.get('production_code'),
                                  'Plot': clean_text(item.get('overview'))}
        listitem["artwork"] = get_image_urls(still=item.get("still_path"))
        listitems.append(listitem)
    return listitems


def handle_misc(results):
    listitems = []
    for item in results:
        listitem = {'label': clean_text(item.get('name')),
                    'path': "plugin://script.extendedinfo?info=listmovies&---id=%s" % item.get('id'),
                    'year': get_year(item.get('release_date')),
                    'Premiered': item.get('release_date'),
                    'Plot': clean_text(item.get('description')),
                    'certification': item.get('certification', "") + item.get('rating', ""),
                    'item_count': item.get('item_count'),
                    'favorite_count': item.get('favorite_count'),
                    'iso_3166_1': item.get('iso_3166_1', "").lower(),
                    'author': item.get('author'),
                    'content': clean_text(item.get('content')),
                    'id': item.get('id'),
                    'url': item.get('url')}
        listitem["artwork"] = get_image_urls(poster=item.get("poster_path"))
        listitems.append(listitem)
    return listitems


def handle_seasons(results):
    listitems = []
    for season in results:
        season_number = season.get('season_number')
        title = LANG(20381) if season_number == 0 else u"%s %s" % (LANG(20373), season_number)
        listitem = {'mediatype': "season",
                    'label': title,
                    'season': season_number,
                    'Premiered': season.get('air_date'),
                    'year': get_year(season.get('air_date'))}
        listitem["properties"] = {'id': season.get('id')}
        listitem["artwork"] = get_image_urls(poster=season.get("poster_path"))
        listitems.append(listitem)
    return listitems


def handle_videos(results):
    listitems = []
    for item in results:
        image = "http://i.ytimg.com/vi/%s/0.jpg" % item.get('key')
        listitem = {'thumb': image,
                    'label': item.get('name'),
                    'size': item.get('size')}
        listitem["properties"] = {'iso_639_1': item.get('iso_639_1'),
                                  'type': item.get('type'),
                                  'key': item.get('key'),
                                  'youtube_id': item.get('key'),
                                  'site': item.get('site'),
                                  'id': item.get('id')}
        listitems.append(listitem)
    return listitems


def handle_people(results):
    people = []
    for item in results:
        person = {'label': item['name'],
                  'mediatype': "actor",
                  'path': "%sextendedactorinfo&&id=%s" % (PLUGIN_BASE, item['id'])}
        person["properties"] = {'adult': item.get('adult'),
                                'alsoknownas': " / ".join(item.get('also_known_as', [])),
                                'biography': clean_text(item.get('biography')),
                                'birthday': item.get('birthday'),
                                'age': calculate_age(item.get('birthday'), item.get('deathday')),
                                'character': item.get('character'),
                                'department': item.get('department'),
                                'job': item.get('job'),
                                'id': item['id'],
                                'cast_id': item.get('cast_id'),
                                'credit_id': item.get('credit_id'),
                                'deathday': item.get('deathday'),
                                'placeofbirth': item.get('place_of_birth'),
                                'homepage': item.get('homepage')}
        person["artwork"] = get_image_urls(profile=item.get("profile_path"))
        people.append(person)
    return people


def handle_images(results):
    images = []
    for item in results:
        image = {}
        image["properties"] = {'aspectratio': item['aspect_ratio'],
                               'vote_average': item.get("vote_average"),
                               'iso_639_1': item.get("iso_639_1")}
        image["artwork"] = get_image_urls(poster=item.get("file_path"))
        if item.get("media"):
            image['title'] = fetch(item["media"], "title")
            image["artwork"]['mediaposter'] = base_url + POSTER_SIZE + fetch(item["media"], "poster_path")
        images.append(image)
    return images


def handle_companies(results):
    companies = []
    for item in results:
        company = {'label': item['name'],
                   'Plot': item['description']}
        company["properties"] = {'parent_company': item['parent_company'],
                                 'headquarters': item['headquarters'],
                                 'homepage': item['homepage'],
                                 'id': item['id'],
                                 'logo_path': item['logo_path']}
        companies.append(company)
    return companies


def search_company(company_name):
    regex = re.compile('\(.+?\)')
    company_name = regex.sub('', company_name)
    params = {"query": company_name}
    response = get_data(url="search/company",
                        params=params,
                        cache_days=10)
    if response and "results" in response:
        return response["results"]
    else:
        log("Could not find company ID for %s" % company_name)
        return ""


def multi_search(search_str):
    params = {"query": search_str}
    response = get_data(url="search/multi",
                        params=params,
                        cache_days=1)
    if response and "results" in response:
        return response["results"]
    else:
        log("Error when searching for %s" % search_str)
        return ""


def get_person_info(person_label, skip_dialog=False):
    if not person_label:
        return False
    params = {"query": person_label.split(" / ")[0],
              "include_adult": include_adult}
    response = get_data(url="search/person",
                        params=params,
                        cache_days=30)
    if not response or "results" not in response:
        return False
    people = [i for i in response["results"] if i["name"] == person_label]
    if len(people) > 1 and not skip_dialog:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        listitem, index = wm.open_selectdialog(listitems=handle_people(people))
        if index >= 0:
            return people[index]
    elif people:
        return people[0]
    elif response["results"]:
        return response["results"][0]
    return False


def get_keyword_id(keyword):
    params = {"query": keyword,
              "include_adult": include_adult}
    response = get_data(url="search/keyword",
                        params=params,
                        cache_days=30)
    if response and "results" in response and response["results"]:
        if len(response["results"]) > 1:
            names = [item["name"] for item in response["results"]]
            selection = xbmcgui.Dialog().select(LANG(32114), names)
            if selection > -1:
                return response["results"][selection]
        elif response["results"]:
            return response["results"][0]
    else:
        log("could not find Keyword ID")
        return False


def get_set_id(set_name):
    params = {"query": set_name.replace("[", "").replace("]", "").replace("Kollektion", "Collection"),
              "language": SETTING("LanguageID")}
    response = get_data(url="search/collection",
                        params=params,
                        cache_days=14)
    if not response or not response.get("results"):
        return ""
    return response["results"][0]["id"]


def get_data(url="", params={}, cache_days=14):
    params["api_key"] = TMDB_KEY
    params = {k: v for k, v in params.items() if v}
    params = {k: unicode(v).encode('utf-8') for k, v in params.items()}
    url = "%s%s?%s" % (URL_BASE, url, urllib.urlencode(params))
    return get_JSON_response(url, cache_days, "TheMovieDB")


def get_company_data(company_id):
    if not company_id:
        return []
    response = get_data(url="company/%s/movies" % (company_id),
                        cache_days=30)
    if response and "results" in response:
        return handle_movies(response["results"])
    else:
        return []


def get_credit_info(credit_id):
    if not credit_id:
        return []
    params = {"language": SETTING("LanguageID")}
    return get_data(url="credit/%s" % (credit_id),
                    params=params,
                    cache_days=30)


def get_account_props(account_states):
    props = {}
    if account_states.get("favorite"):
        props["FavButton_Label"] = LANG(32155)
        props["favorite"] = "True"
    else:
        props["FavButton_Label"] = LANG(32154)
        props["favorite"] = ""
    if account_states["rated"]:
        props["rated"] = str(account_states["rated"]["value"])
    else:
        props["rated"] = ""
    if "watchlist" in account_states:
        props["watchlist"] = str(account_states["watchlist"])
    return props


def get_image_urls(poster=None, still=None, fanart=None, profile=None):
    images = {}
    if poster:
        images["poster"] = base_url + "w500" + poster
        images["poster_original"] = base_url + "original" + poster
        images["original"] = base_url + "original" + poster
        images["poster_small"] = base_url + "w342" + poster
        images["thumb"] = base_url + "w342" + poster
    if still:
        images["thumb"] = base_url + "w300" + still
        images["still"] = base_url + "w300" + still
        images["still_original"] = base_url + "original" + still
        images["still_small"] = base_url + "w185" + still
    if fanart:
        images["fanart"] = base_url + "w1280" + fanart
        images["fanart_original"] = base_url + "original" + fanart
        images["original"] = base_url + "original" + fanart
        images["fanart_small"] = base_url + "w780" + fanart
    if profile:
        images["poster"] = base_url + "w500" + profile
        images["poster_original"] = base_url + "original" + profile
        images["poster_small"] = base_url + "w342" + profile
        images["thumb"] = base_url + "w342" + profile
    return images


def get_movie_tmdb_id(imdb_id=None, name=None, dbid=None):
    if dbid and (int(dbid) > 0):
        movie_id = local_db.get_imdb_id("movie", dbid)
        log("IMDB Id from local DB: %s" % (movie_id))
        return movie_id
    elif imdb_id:
        params = {"external_source": "imdb_id",
                  "language": SETTING("LanguageID")}
        response = get_data(url="find/tt%s" % (imdb_id.replace("tt", "")),
                            params=params)
        if response and response["movie_results"]:
            return response["movie_results"][0]["id"]
    if name:
        return search_media(name)
    else:
        return None


def get_show_tmdb_id(tvdb_id=None, source="tvdb_id"):
    params = {"external_source": source,
              "language": SETTING("LanguageID")}
    response = get_data(url="find/%s" % (tvdb_id),
                        params=params)
    if response and response["tv_results"]:
        return response["tv_results"][0]["id"]
    else:
        notify("TVShow Info not available.")
        return None


def get_trailer(movie_id):
    response = get_full_movie(movie_id)
    if response and "videos" in response and response['videos']['results']:
        return response['videos']['results'][0]['key']
    notify("Could not get trailer")
    return ""


def extended_movie_info(movie_id=None, dbid=None, cache_time=14):
    if not movie_id:
        return None
    params = {"append_to_response": ALL_MOVIE_PROPS,
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    if Login.check_login():
        params["session_id"] = Login.get_session_id()
    response = get_data(url="movie/%s" % (movie_id),
                        params=params,
                        cache_days=cache_time)
    if not response:
        notify("Could not get movie information")
        return {}
    mpaa = ""
    set_name = ""
    set_id = ""
    genres = [i["name"] for i in response["genres"]]
    Studio = [i["name"] for i in response["production_companies"]]
    authors = [i["name"] for i in response['credits']['crew'] if i["department"] == "Writing"]
    directors = [i["name"] for i in response['credits']['crew'] if i["department"] == "Directing"]
    us_cert = dictfind(response['releases']['countries'], "iso_3166_1", "US")
    if us_cert:
        mpaa = us_cert["certification"]
    elif response['releases']['countries']:
        mpaa = response['releases']['countries'][0]['certification']
    movie_set = fetch(response, "belongs_to_collection")
    if movie_set:
        set_name = fetch(movie_set, "name")
        set_id = fetch(movie_set, "id")
    artwork = get_image_urls(poster=response.get("poster_path"),
                             fanart=response.get("backdrop_path"))
    path = PLUGIN_BASE + 'youtubevideo&&id=%s' % fetch(response, "id")
    movie = {'title': fetch(response, 'title'),
             'label': fetch(response, 'title'),
             'path': path,
             'Tagline': fetch(response, 'tagline'),
             'duration': fetch(response, 'runtime'),
             'mpaa': mpaa,
             'Director': " / ".join(directors),
             'writer': " / ".join(authors),
             'Plot': clean_text(fetch(response, 'overview')),
             'OriginalTitle': fetch(response, 'original_title'),
             'Country': fetch(response, 'original_language'),
             'genre': " / ".join(genres),
             'Rating': fetch(response, 'vote_average'),
             'Premiered': fetch(response, 'release_date'),
             'Votes': fetch(response, 'vote_count'),
             'Adult': str(fetch(response, 'adult')),
             'Popularity': fetch(response, 'popularity'),
             'Status': translate_status(fetch(response, 'status')),
             'Set': set_name,
             'SetId': set_id,
             'id': fetch(response, 'id'),
             'imdb_id': fetch(response, 'imdb_id'),
             'duration(h)': format_time(fetch(response, 'runtime'), "h"),
             'duration(m)': format_time(fetch(response, 'runtime'), "m"),
             'Budget': millify(fetch(response, 'budget')),
             'Revenue': millify(fetch(response, 'revenue')),
             'Homepage': fetch(response, 'homepage'),
             'Studio': " / ".join(Studio),
             'year': get_year(fetch(response, 'release_date'))}
    movie.update(artwork)
    videos = handle_videos(response["videos"]["results"]) if "videos" in response else []
    account_states = response.get("account_states")
    if dbid:
        local_item = local_db.get_movie(dbid)
        movie.update(local_item)
    else:
        movie = local_db.merge_with_local_movie_info([movie])[0]
    movie['Rating'] = fetch(response, 'vote_average')  # hack to get tmdb rating instead of local one
    listitems = {"actors": handle_people(response["credits"]["cast"]),
                 "similar": handle_movies(response["similar"]["results"]),
                 "lists": handle_misc(response["lists"]["results"]),
                 "studios": handle_misc(response["production_companies"]),
                 "releases": handle_misc(response["releases"]["countries"]),
                 "crew": handle_people(response["credits"]["crew"]),
                 "genres": handle_misc(response["genres"]),
                 "keywords": handle_misc(response["keywords"]["keywords"]),
                 "reviews": handle_misc(response["reviews"]["results"]),
                 "videos": videos,
                 "images": handle_images(response["images"]["posters"]),
                 "backdrops": handle_images(response["images"]["backdrops"])}
    return (movie, listitems, account_states)


def extended_tvshow_info(tvshow_id=None, cache_time=7, dbid=None):
    if not tvshow_id:
        return None
    params = {"append_to_response": ALL_TV_PROPS,
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    if Login.check_login():
        params["session_id"] = Login.get_session_id()
    response = get_data(url="tv/%s" % (tvshow_id),
                        params=params,
                        cache_days=cache_time)
    if not response:
        return False
    account_states = response.get("account_states")
    videos = handle_videos(response["videos"]["results"]) if "videos" in response else []
    tmdb_id = fetch(response, 'id')
    artwork = get_image_urls(poster=response.get("poster_path"),
                             fanart=response.get("backdrop_path"))
    if len(response.get("episode_run_time", -1)) > 1:
        duration = "%i - %i" % (min(response["episode_run_time"]), max(response["episode_run_time"]))
    elif len(response.get("episode_run_time", -1)) == 1:
        duration = "%i" % (response["episode_run_time"][0])
    else:
        duration = ""
    us_cert = dictfind(response['content_ratings']['results'], "iso_3166_1", "US")
    if us_cert:
        mpaa = us_cert["rating"]
    elif response['content_ratings']['results']:
        mpaa = response['content_ratings']['results'][0]['rating']
    else:
        mpaa = ""
    genres = [item["name"] for item in response["genres"]]
    tvshow = {'title': response.get('name'),
              'TVShowTitle': response.get('name'),
              'OriginalTitle': response.get('original_name', ""),
              'duration': duration,
              'duration(h)': format_time(duration, "h"),
              'duration(m)': format_time(duration, "m"),
              'id': tmdb_id,
              'mpaa': mpaa,
              'genre': " / ".join(genres),
              'credit_id': response.get('credit_id'),
              'Plot': clean_text(response.get("overview")),
              'year': get_year(response.get('first_air_date')),
              'mediatype': "tvshow",
              'path': PLUGIN_BASE + 'extendedtvinfo&&id=%s' % tmdb_id,
              'Popularity': response.get('popularity'),
              'Rating': response.get('vote_average'),
              'country': response.get('original_language'),
              'User_Rating': response.get('rating'),
              'Votes': response.get('vote_count'),
              'Status': translate_status(response.get('status')),
              'ShowType': response.get('type'),
              'homepage': response.get('homepage'),
              'last_air_date': response.get('last_air_date'),
              'TotalEpisodes': response.get('number_of_episodes'),
              'TotalSeasons': response.get('number_of_seasons'),
              'in_production': response.get('in_production'),
              'Premiered': response.get('first_air_date')}
    tvshow.update(artwork)
    if dbid:
        local_item = local_db.get_tvshow(dbid)
        tvshow.update(local_item)
    else:
        tvshow = local_db.merge_with_local_tvshow_info([tvshow])[0]
    tvshow['Rating'] = fetch(response, 'vote_average')  # hack to get tmdb rating instead of local one
    listitems = {"actors": handle_people(response["credits"]["cast"]),
                 "similar": handle_tvshows(response["similar"]["results"]),
                 "studios": handle_misc(response["production_companies"]),
                 "networks": handle_misc(response["networks"]),
                 "certifications": handle_misc(response["content_ratings"]["results"]),
                 "crew": handle_people(response["credits"]["crew"]),
                 "genres": handle_misc(response["genres"]),
                 "keywords": handle_misc(response["keywords"]["results"]),
                 "videos": videos,
                 "seasons": handle_seasons(response["seasons"]),
                 "images": handle_images(response["images"]["posters"]),
                 "backdrops": handle_images(response["images"]["backdrops"])}
    return (tvshow, listitems, account_states)


def extended_season_info(tvshow_id, season_number):
    if not tvshow_id or not season_number:
        return None
    params = {"append_to_response": ALL_TV_PROPS,
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    if Login.check_login():
        params["session_id"] = Login.get_session_id()
    tvshow = get_data(url="tv/%s" % (tvshow_id),
                      params=params,
                      cache_days=99999)
    params = {"append_to_response": ALL_SEASON_PROPS,
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    response = get_data(url="tv/%s/season/%s" % (tvshow_id, season_number),
                        params=params,
                        cache_days=7)
    if not response:
        notify("Could not find season info")
        return None
    if response.get("name", False):
        title = response["name"]
    elif season_number == "0":
        title = LANG(20381)
    else:
        title = "%s %s" % (LANG(20373), season_number)
    season = {'SeasonDescription': clean_text(response["overview"]),
              'Plot': clean_text(response["overview"]),
              'TVShowTitle': fetch(tvshow, 'name'),
              'title': title,
              'Premiered': response["air_date"]}
    artwork = get_image_urls(poster=response.get("poster_path"))
    season.update(artwork)
    videos = handle_videos(response["videos"]["results"]) if "videos" in response else []
    listitems = {"actors": handle_people(response["credits"]["cast"]),
                 "crew": handle_people(response["credits"]["crew"]),
                 "videos": videos,
                 "episodes": handle_episodes(response["episodes"]),
                 "images": handle_images(response["images"]["posters"]),
                 "backdrops": handle_images(response["images"].get("backdrops", []))}
    return (season, listitems)


def extended_episode_info(tvshow_id, season, episode, cache_time=7):
    if not tvshow_id or not episode:
        return None
    if not season:
        season = 0
    params = {"append_to_response": ALL_EPISODE_PROPS,
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    if Login.check_login():
        params["session_id"] = Login.get_session_id()
    response = get_data(url="tv/%s/season/%s/episode/%s" % (tvshow_id, season, episode),
                        params=params,
                        cache_days=cache_time)
    videos = []
    if "videos" in response:
        videos = handle_videos(response["videos"]["results"])
    answer = {"actors": handle_people(response["credits"]["cast"]),
              "crew": handle_people(response["credits"]["crew"]),
              "guest_stars": handle_people(response["credits"]["guest_stars"]),
              "videos": videos,
              "images": handle_images(response["images"]["stills"])}
    return (handle_episodes([response])[0], answer, response.get("account_states"))


def extended_actor_info(actor_id):
    if not actor_id:
        return None
    response = get_data(url="person/%s" % (actor_id),
                        params={"append_to_response": ALL_ACTOR_PROPS},
                        cache_days=1)
    tagged_images = []
    if "tagged_images" in response:
        tagged_images = handle_images(response["tagged_images"]["results"])
    listitems = {"movie_roles": handle_movies(response["movie_credits"]["cast"]),
                 "tvshow_roles": handle_tvshows(response["tv_credits"]["cast"]),
                 "movie_crew_roles": handle_movies(response["movie_credits"]["crew"]),
                 "tvshow_crew_roles": handle_tvshows(response["tv_credits"]["crew"]),
                 "tagged_images": tagged_images,
                 "images": handle_images(response["images"]["profiles"])}
    info = {'adult': response.get('adult'),
            'label': response['name'],
            'alsoknownas': " / ".join(response.get('also_known_as', [])),
            'biography': clean_text(response.get('biography')),
            'birthday': response.get('birthday'),
            'age': calculate_age(response.get('birthday'), response.get('deathday')),
            'character': response.get('character'),
            'department': response.get('department'),
            'job': response.get('job'),
            'mediatype': "actor",
            'id': response['id'],
            'cast_id': response.get('cast_id'),
            'credit_id': response.get('credit_id'),
            'path': "%sextendedactorinfo&&id=%s" % (PLUGIN_BASE, response['id']),
            'deathday': response.get('deathday'),
            'placeofbirth': response.get('place_of_birth'),
            'homepage': response.get('homepage')}
    artwork = get_image_urls(profile=response.get("profile_path"))
    info.update(artwork)
    info["DBMovies"] = str(len([d for d in listitems["movie_roles"] if "dbid" in d]))
    return (info, listitems)


def translate_status(status_string):
    translations = {"released": LANG(32071),
                    "post production": LANG(32072),
                    "in production": LANG(32073),
                    "ended": LANG(32074),
                    "returning series": LANG(32075),
                    "planned": LANG(32076)}
    if status_string.lower() in translations:
        return translations[status_string.lower()]
    else:
        return status_string


def get_movie_lists(movie_id):
    response = get_full_movie(movie_id)
    return handle_misc(response["lists"]["results"])


def get_rated_media_items(media_type):
    '''takes "tv/episodes", "tv" or "movies"'''
    if Login.check_login():
        session_id = Login.get_session_id()
        account_id = Login.get_account_id()
        if not session_id:
            notify("Could not get session id")
            return []
        params = {"session_id": session_id,
                  "language": SETTING("LanguageID")}
        response = get_data(url="account/%s/rated/%s" % (account_id, media_type),
                            params=params,
                            cache_days=0)
    else:
        session_id = Login.get_guest_session_id()
        if not session_id:
            notify("Could not get session id")
            return []
        params = {"language": SETTING("LanguageID")}
        response = get_data(url="guest_session/%s/rated_movies" % (session_id),
                            params=params,
                            cache_days=0)
    if media_type == "tv/episodes":
        return handle_episodes(response["results"])
    elif media_type == "tv":
        return handle_tvshows(response["results"], False, None)
    else:
        return handle_movies(response["results"], False, None)


def get_fav_items(media_type):
    '''takes "tv/episodes", "tv" or "movies"'''
    session_id = Login.get_session_id()
    account_id = Login.get_account_id()
    if not session_id:
        notify("Could not get session id")
        return []
    params = {"session_id": session_id,
              "language": SETTING("LanguageID")}
    response = get_data(url="account/%s/favorite/%s" % (account_id, media_type),
                        params=params,
                        cache_days=0)
    if "results" in response:
        if media_type == "tv":
            return handle_tvshows(response["results"], False, None)
        elif media_type == "tv/episodes":
            return handle_episodes(response["results"])
        else:
            return handle_movies(response["results"], False, None)
    else:
        return []


def get_movies_from_list(list_id, cache_time=5):
    '''
    get movie dict list from tmdb list.
    '''
    response = get_data(url="list/%s" % (list_id),
                        params={"language": SETTING("LanguageID")},
                        cache_days=cache_time)
    return handle_movies(response["items"], False, None)


def get_popular_actors():
    '''
    get dict list containing popular actors / directors / writers
    '''
    response = get_data(url="person/popular",
                        cache_days=1)
    return handle_people(response["results"])


def get_actor_credits(actor_id, media_type):
    '''
    media_type: movie or tv
    '''
    response = get_data(url="person/%s/%s_credits" % (actor_id, media_type),
                        cache_days=1)
    return handle_movies(response["cast"])


def get_full_movie(movie_id):
    params = {"include_image_language": "en,null,%s" % SETTING("LanguageID"),
              "language": SETTING("LanguageID"),
              "append_to_response": ALL_MOVIE_PROPS
              }
    return get_data(url="movie/%s" % (movie_id),
                    params=params,
                    cache_days=30)


def get_keywords(movie_id):
    '''
    get dict list containing movie keywords
    '''
    response = get_full_movie(movie_id)
    keywords = []
    if "keywords" in response:
        for keyword in response["keywords"]["keywords"]:
            keywords.append({'id': fetch(keyword, 'id'),
                            'label': keyword['name']})
    return keywords


def get_similar_movies(movie_id):
    '''
    get dict list containing movies similar to *movie_id
    '''
    response = get_full_movie(movie_id)
    if "similar" in response:
        return handle_movies(response["similar"]["results"])
    else:
        return []


def get_similar_tvshows(tvshow_id):
    '''
    return list with similar tvshows for show with *tvshow_id (TMDB ID)
    '''
    params = {"append_to_response": ALL_TV_PROPS,
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    if Login.check_login():
        params["session_id"] = Login.get_session_id()
    response = get_data(url="tv/%s" % (tvshow_id),
                        params=params,
                        cache_days=10)
    if "similar" in response:
        return handle_tvshows(response["similar"]["results"])
    else:
        return []


def get_tmdb_shows(tvshow_type):
    '''
    return list with tv shows
    available types: airing, on_the_air, top_rated, popular
    '''
    params = {"language": SETTING("LanguageID")}
    response = get_data(url="tv/%s" % (tvshow_type),
                        params=params,
                        cache_days=0.3)
    if "results" in response:
        return handle_tvshows(response["results"], False, None)
    else:
        return []


def get_tmdb_movies(movie_type):
    '''
    return list with movies
    available types: now_playing, upcoming, top_rated, popular
    '''
    params = {"language": SETTING("LanguageID")}
    response = get_data(url="movie/%s" % (movie_type),
                        params=params,
                        cache_days=0.3)
    if "results" in response:
        return handle_movies(response["results"], False, None)
    else:
        return []


def get_set_movies(set_id):
    '''
    return list with movies which are part of set with *set_id
    '''
    params = {"append_to_response": "images",
              "language": SETTING("LanguageID"),
              "include_image_language": "en,null,%s" % SETTING("LanguageID")}
    response = get_data(url="collection/%s" % (set_id),
                        params=params,
                        cache_days=14)
    if response:
        artwork = get_image_urls(poster=response.get("poster_path"),
                                 fanart=response.get("backdrop_path"))
        info = {"label": response["name"],
                "overview": response["overview"],
                "id": response["id"]}
        info.update(artwork)
        return handle_movies(response.get("parts", [])), info
    else:
        return [], {}


def get_person_movies(person_id):
    params = {"language": SETTING("LanguageID")}
    response = get_data(url="person/%s/credits" % (person_id),
                        params=params,
                        cache_days=14)
    # return handle_movies(response["crew"]) + handle_movies(response["cast"])
    if "crew" in response:
        return handle_movies(response["crew"])
    else:
        return []


def search_media(media_name=None, year='', media_type="movie", cache_days=1):
    '''
    return list of items with type *media_type for search with *media_name
    '''
    if not media_name:
        return None
    params = {"query": "%s %s" % (media_name, year),
              "language": SETTING("language"),
              "include_adult": include_adult}
    response = get_data(url="search/%s" % (media_type),
                        params=params,
                        cache_days=cache_days)
    if not response == "Empty":
        for item in response['results']:
            if item['id']:
                return item['id']
    return None

Login = LoginProvider(username=SETTING("tmdb_username"),
                      password=SETTING("tmdb_password"))
