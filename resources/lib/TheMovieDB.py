# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from YouTube import *
from Utils import *
from local_db import *
import threading
import re
from urllib2 import Request, urlopen

TMDB_KEY = '34142515d9d23817496eeb4ff1d223d0'
POSTER_SIZES = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]
LOGO_SIZES = ["w45", "w92", "w154", "w185", "w300", "w500", "original"]
BACKDROP_SIZES = ["w300", "w780", "w1280", "original"]
PROFILE_SIZES = ["w45", "w185", "h632", "original"]
STILL_SIZES = ["w92", "w185", "w300", "original"]
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-agent': 'XBMC/14.0 ( phil65@kodi.tv )'
}
base_url = ""
poster_size = ""
fanart_size = ""
include_adult = str(ADDON.getSetting("include_adults")).lower()
if ADDON.getSetting("use_https"):
    URL_BASE = "https://api.themoviedb.org/3/"
else:
    URL_BASE = "http://api.themoviedb.org/3/"


def check_login():
    if ADDON.getSetting("tmdb_username"):
        session_id = get_session_id()
        if session_id:
            return "True"
    return ""


def get_rating_from_user():
    ratings = []
    for i in range(1, 21):
        ratings.append(str(float(i * 0.5)))
    rating = xbmcgui.Dialog().select(ADDON.getLocalizedString(32129), ratings)
    if rating > -1:
        return (float(rating) * 0.5) + 0.5
    else:
        return None


def send_rating_for_media_item(media_type, media_id, rating):
    # media_type: movie, tv or episode
    # media_id: tmdb_id / episode ident array
    # rating: ratung value (0.5-10.0, 0.5 steps)
    if check_login():
        session_id_string = "session_id=" + get_session_id()
    else:
        session_id_string = "guest_session_id=" + get_guest_session_id()
    values = '{"value": %.1f}' % rating
    if media_type == "episode":
        url = URL_BASE + "tv/%s/season/%s/episode/%s/rating?api_key=%s&%s" % (str(media_id[0]), str(media_id[1]), str(media_id[2]), TMDB_KEY, session_id_string)
    else:
        url = URL_BASE + "%s/%s/rating?api_key=%s&%s" % (media_type, str(media_id), TMDB_KEY, session_id_string)
    request = Request(url, data=values, headers=HEADERS)
    response = urlopen(request).read()
    results = simplejson.loads(response)
    notify(ADDON_NAME, results["status_message"])


def change_fav_status(media_id=None, media_type="movie", status="true"):
    session_id = get_session_id()
    account_id = get_account_info()
    values = '{"media_type": "%s", "media_id": %s, "favorite": %s}' % (media_type, str(media_id), status)
    if not session_id:
        notify("Could not get session id")
        return None
    url = URL_BASE + "account/%s/favorite?session_id=%s&api_key=%s" % (str(account_id), session_id, TMDB_KEY)
    request = Request(url, data=values, headers=HEADERS)
    response = urlopen(request).read()
    results = simplejson.loads(response)
    notify(ADDON_NAME, results["status_message"])


def create_list(list_name):
    session_id = get_session_id()
    url = URL_BASE + "list?api_key=%s&session_id=%s" % (TMDB_KEY, session_id)
    values = {'name': '%s' % list_name, 'description': 'List created by ExtendedInfo Script for Kodi.'}
    request = Request(url, data=simplejson.dumps(values), headers=HEADERS)
    response = urlopen(request).read()
    results = simplejson.loads(response)
    notify(ADDON_NAME, results["status_message"])
    return results["list_id"]


def remove_list(list_id):
    session_id = get_session_id()
    url = URL_BASE + "list/%s?api_key=%s&session_id=%s" % (list_id, TMDB_KEY, session_id)
    log("Remove List: " + url)
    values = {'media_id': list_id}
    request = Request(url, data=simplejson.dumps(values), headers=HEADERS)
    request.get_method = lambda: 'DELETE'
    response = urlopen(request).read()
    results = simplejson.loads(response)
    notify(ADDON_NAME, results["status_message"])
    return results["list_id"]


def change_list_status(list_id, movie_id, status):
    if status:
        method = "add_item"
    else:
        method = "remove_item"
    session_id = get_session_id()
    url = URL_BASE + "list/%s/%s?api_key=%s&session_id=%s" % (list_id, method, TMDB_KEY, session_id)
    log(url)
    values = {'media_id': movie_id}
    request = Request(url, data=simplejson.dumps(values), headers=HEADERS)
    try:
        response = urlopen(request).read()
    except urllib2.HTTPError as err:
        if err.code == 401:
            notify("Error", "Not authorized to modify list")
    results = simplejson.loads(response)
    notify(ADDON_NAME, results["status_message"])


def get_account_lists(cache_time=0):
    session_id = get_session_id()
    account_id = get_account_info()
    if session_id and account_id:
        response = get_tmdb_data("account/%s/lists?session_id=%s&" % (str(account_id), session_id), cache_time)
        return response["results"]
    else:
        return []


def get_account_info():
    session_id = get_session_id()
    response = get_tmdb_data("account?session_id=%s&" % session_id, 999999)
    if "id" in response:
        return response["id"]
    else:
        return None


def get_certification_list(media_type):
    response = get_tmdb_data("certification/%s/list?" % media_type, 999999)
    if "certifications" in response:
        return response["certifications"]
    else:
        return []


def get_guest_session_id():
    response = get_tmdb_data("authentication/guest_session/new?", 999999)
    if "guest_session_id" in response:
        return str(response["guest_session_id"])
    else:
        return None


def get_session_id():
    request_token = auth_request_token()
    response = get_tmdb_data("authentication/session/new?request_token=%s&" % request_token, 99999)
    if response and "success" in response:
        pass_dict_to_skin({"tmdb_logged_in": "true"})
        return str(response["session_id"])
    else:
        pass_dict_to_skin({"tmdb_logged_in": ""})
        notify("login failed")
        return None


def get_request_token():
    response = get_tmdb_data("authentication/token/new?", 999999)
    return response["request_token"]


def auth_request_token():
    request_token = get_request_token()
    username = ADDON.getSetting("tmdb_username")
    password = ADDON.getSetting("tmdb_password")
    response = get_tmdb_data("authentication/token/validate_with_login?request_token=%s&username=%s&password=%s&" % (request_token, username, password), 999999)
    if "success" in response and response["success"]:
        return response["request_token"]
    else:
        return None


def handle_tmdb_multi_search(results=[]):
    listitems = []
    for item in results:
        if item["media_type"] == "movie":
            listitem = handle_tmdb_movies([item])[0]
        elif item["media_type"] == "tv":
            listitem = handle_tmdb_tvshows([item])[0]
        else:
            listitem = handle_tmdb_people([item])[0]
        listitems.append(listitem)
    return listitems


def handle_tmdb_movies(results=[], local_first=True, sortkey="year"):
    response = get_tmdb_data("genre/movie/list?language=%s&" % (ADDON.getSetting("LanguageID")), 9999)
    id_list = [item["id"] for item in response["genres"]]
    label_list = [item["name"] for item in response["genres"]]
    movies = []
    log("starting handle_tmdb_movies")
    for movie in results:
        if "genre_ids" in movie:
            genres = " / ".join([label_list[id_list.index(genre_id)] for genre_id in movie["genre_ids"]])
        else:
            genres = ""
        tmdb_id = str(fetch(movie, 'id'))
        artwork = get_image_urls(poster=movie.get("poster_path"), fanart=movie.get("backdrop_path"))
        trailer = "plugin://script.extendedinfo/?info=playtrailer&&id=" + tmdb_id
        if ADDON.getSetting("infodialog_onclick") != "false":
            # path = 'plugin://script.extendedinfo/?info=extendedinfo&&id=%s' % tmdb_id
            path = 'plugin://script.extendedinfo/?info=action&&id=RunScript(script.extendedinfo,info=extendedinfo,id=%s)' % tmdb_id
        else:
            path = trailer
        listitem = {'Art(fanart)': artwork.get("fanart", ""),
                    'Art(poster)': artwork.get("poster_small", ""),
                    'thumb': artwork.get("poster_small", ""),
                    'Poster': artwork.get("poster_small", ""),
                    'fanart': artwork.get("fanart", ""),
                    'title': fetch(movie, 'title'),
                    'Label': fetch(movie, 'title'),
                    'OriginalTitle': fetch(movie, 'original_title'),
                    'id': tmdb_id,
                    'path': path,
                    'media_type': "movie",
                    'country': fetch(movie, 'original_language'),
                    'plot': fetch(movie, 'overview'),
                    'Trailer': trailer,
                    'Rating': fetch(movie, 'vote_average'),
                    'credit_id': fetch(movie, 'credit_id'),
                    'character': fetch(movie, 'character'),
                    'job': fetch(movie, 'job'),
                    'department': fetch(movie, 'department'),
                    'Votes': fetch(movie, 'vote_count'),
                    'User_Rating': fetch(movie, 'rating'),
                    'year': get_year(fetch(movie, 'release_date')),
                    'Genre': genres,
                    'time_comparer': fetch(movie, 'release_date').replace("-", ""),
                    'Premiered': fetch(movie, 'release_date')}
        movies.append(listitem)
    movies = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in movies)]
    movies = merge_with_local_movie_info(movies, local_first, sortkey)
    return movies


def handle_tmdb_tvshows(results, local_first=True, sortkey="year"):
    tvshows = []
    log("starting handle_tmdb_tvshows")
    for tv in results:
        tmdb_id = fetch(tv, 'id')
        duration = ""
        artwork = get_image_urls(poster=tv.get("poster_path"), fanart=tv.get("backdrop_path"))
        if "episode_run_time" in tv:
            if len(tv["episode_run_time"]) > 1:
                duration = "%i - %i" % (min(tv["episode_run_time"]), max(tv["episode_run_time"]))
            elif len(tv["episode_run_time"]) == 1:
                duration = "%i" % (tv["episode_run_time"][0])
            else:
                duration = ""
        newtv = {'Art(fanart)': artwork.get("fanart", ""),
                 'Art(poster)': artwork.get("poster", ""),
                 'thumb': artwork.get("poster", ""),
                 'Poster': artwork.get("poster", ""),
                 'fanart': artwork.get("fanart", ""),
                 'title': fetch(tv, 'name'),
                 'TVShowTitle': fetch(tv, 'name'),
                 'OriginalTitle': fetch(tv, 'original_name'),
                 'duration': duration,
                 'id': tmdb_id,
                 'credit_id': fetch(tv, 'credit_id'),
                 'Plot': fetch(tv, "overview"),
                 'year': get_year(fetch(tv, 'first_air_date')),
                 'media_type': "tv",
                 'path': 'plugin://script.extendedinfo/?info=action&&id=RunScript(script.extendedinfo,info=extendedtvinfo,id=%s)' % tmdb_id,
                 # 'path': 'plugin://script.extendedinfo/?info=extendedtvinfo&&id=%s' % tmdb_id,
                 'Rating': fetch(tv, 'vote_average'),
                 'User_Rating': str(fetch(tv, 'rating')),
                 'Votes': fetch(tv, 'vote_count'),
                 'number_of_episodes': fetch(tv, 'number_of_episodes'),
                 'number_of_seasons': fetch(tv, 'number_of_seasons'),
                 'Release_Date': fetch(tv, 'first_air_date'),
                 'ReleaseDate': fetch(tv, 'first_air_date'),
                 'Premiered': fetch(tv, 'first_air_date')}
        tvshows.append(newtv)
    tvshows = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in tvshows)]
    tvshows = merge_with_local_tvshow_info(tvshows, local_first, sortkey)
    return tvshows


def handle_tmdb_episodes(results):
    listitems = []
    for item in results:
        artwork = get_image_urls(still=item.get("still_path"))
        listitem = {'Art(poster)': artwork.get("still", ""),
                    'Poster': artwork.get("still", ""),
                    'media_type': "episode",
                    'thumb': artwork.get("still_small", ""),
                    'title': clean_text(fetch(item, 'name')),
                    'release_date': fetch(item, 'air_date'),
                    'episode': fetch(item, 'episode_number'),
                    'production_code': fetch(item, 'production_code'),
                    'season': fetch(item, 'season_number'),
                    'Rating': fetch(item, 'vote_average'),
                    'Votes': fetch(item, 'vote_count'),
                    'id': fetch(item, 'id'),
                    'Description': clean_text(fetch(item, 'overview'))}
        listitems.append(listitem)
    return listitems


def handle_tmdb_misc(results):
    listitems = []
    for item in results:
        artwork = get_image_urls(poster=item.get("poster_path"))
        listitem = {'Art(poster)': artwork.get("poster", ""),
                    'Poster': artwork.get("poster", ""),
                    'thumb': artwork.get("poster_small", ""),
                    'title': clean_text(fetch(item, 'name')),
                    'certification': fetch(item, 'certification') + fetch(item, 'rating'),
                    'item_count': fetch(item, 'item_count'),
                    'favorite_count': fetch(item, 'favorite_count'),
                    'release_date': fetch(item, 'release_date'),
                    'path': "plugin://script.extendedinfo?info=listmovies&---id=%s" % fetch(item, 'id'),
                    'year': get_year(fetch(item, 'release_date')),
                    'iso_3166_1': fetch(item, 'iso_3166_1'),
                    'author': fetch(item, 'author'),
                    'content': clean_text(fetch(item, 'content')),
                    'id': fetch(item, 'id'),
                    'url': fetch(item, 'url'),
                    'Description': clean_text(fetch(item, 'description'))}
        listitems.append(listitem)
    return listitems


def handle_tmdb_seasons(results):
    listitems = []
    for season in results:
        season_number = str(fetch(season, 'season_number'))
        artwork = get_image_urls(poster=season.get("poster_path"))
        if season_number == "0":
            title = "Specials"
        else:
            title = "Season %s" % season_number
        listitem = {'Art(poster)': artwork.get("poster", ""),
                    'Poster': artwork.get("poster", ""),
                    'media_type': "season",
                    'thumb': artwork.get("poster_small", ""),
                    'title': title,
                    'season': season_number,
                    'air_date': fetch(season, 'air_date'),
                    'year': get_year(fetch(season, 'air_date')),
                    'id': fetch(season, 'id')}
        listitems.append(listitem)
    return listitems


def handle_tmdb_videos(results):
    listitems = []
    for item in results:
        image = "http://i.ytimg.com/vi/" + fetch(item, 'key') + "/0.jpg"
        listitem = {'thumb': image,
                    'title': fetch(item, 'name'),
                    'iso_639_1': fetch(item, 'iso_639_1'),
                    'type': fetch(item, 'type'),
                    'key': fetch(item, 'key'),
                    'youtube_id': fetch(item, 'key'),
                    'site': fetch(item, 'site'),
                    'id': fetch(item, 'id'),
                    'size': fetch(item, 'size')}
        listitems.append(listitem)
    return listitems


def handle_tmdb_people(results):
    people = []
    for person in results:
        builtin = 'RunScript(script.extendedinfo,info=extendedactorinfo,id=%s)' % str(person['id'])
        artwork = get_image_urls(profile=person.get("profile_path"))
        also_known_as = " / ".join(fetch(person, 'also_known_as'))
        newperson = {'adult': str(fetch(person, 'adult')),
                     'name': person['name'],
                     'title': person['name'],
                     'also_known_as': also_known_as,
                     'alsoknownas': also_known_as,
                     'biography': clean_text(fetch(person, 'biography')),
                     'birthday': fetch(person, 'birthday'),
                     'age': calculate_age(fetch(person, 'birthday'), fetch(person, 'deathday')),
                     'character': fetch(person, 'character'),
                     'department': fetch(person, 'department'),
                     'job': fetch(person, 'job'),
                     'media_type': "person",
                     'id': str(person['id']),
                     'cast_id': str(fetch(person, 'cast_id')),
                     'credit_id': str(fetch(person, 'credit_id')),
                     'path': "plugin://script.extendedinfo/?info=action&&id=" + builtin,
                     'deathday': fetch(person, 'deathday'),
                     'place_of_birth': fetch(person, 'place_of_birth'),
                     'placeofbirth': fetch(person, 'place_of_birth'),
                     'homepage': fetch(person, 'homepage'),
                     'thumb': artwork.get("profile_small", ""),
                     'icon': artwork.get("profile_small", ""),
                     'poster': artwork.get("profile", "")}
        people.append(newperson)
    return people


def handle_tmdb_images(results):
    images = []
    for item in results:
        image = {'aspectratio': item['aspect_ratio'],
                 'thumb': base_url + "w342" + item['file_path'],
                 'vote_average': fetch(item, "vote_average"),
                 'iso_639_1': fetch(item, "iso_639_1"),
                 'poster': base_url + poster_size + item['file_path'],
                 'original': base_url + "original" + item['file_path']}
        images.append(image)
    return images


def handle_tmdb_tagged_images(results):
    images = []
    for item in results:
        image = {'aspectratio': item['aspect_ratio'],
                 'thumb': base_url + "w342" + item['file_path'],
                 'vote_average': fetch(item, "vote_average"),
                 'iso_639_1': fetch(item, "iso_639_1"),
                 'title': fetch(item["media"], "title"),
                 'mediaposter': base_url + poster_size + fetch(item["media"], "poster_path"),
                 'poster': base_url + poster_size + item['file_path'],
                 'original': base_url + "original" + item['file_path']}
        images.append(image)
    return images


def handle_tmdb_companies(results):
    companies = []
    log("starting HandleLastFMCompanyResult")
    for company in results:
        newcompany = {'parent_company': company['parent_company'],
                      'name': company['name'],
                      'description': company['description'],
                      'headquarters': company['headquarters'],
                      'homepage': company['homepage'],
                      'id': company['id'],
                      'logo_path': company['logo_path']}
        companies.append(newcompany)
    return companies


def search_company(company_name):
    import re
    regex = re.compile('\(.+?\)')
    company_name = regex.sub('', company_name)
    response = get_tmdb_data("search/company?query=%s&" % url_quote(company_name), 10)
    try:
        return response["results"]
    except:
        log("Could not find company ID for %s" % company_name)
        return ""


def multi_search(search_string):
    response = get_tmdb_data("search/multi?query=%s&" % url_quote(search_string), 1)
    if response and "results" in response:
        return response["results"]
    else:
        log("Error when searching for %s" % search_string)
        return ""


def get_person_info(person_label, skip_dialog=False):
    persons = person_label.split(" / ")
    response = get_tmdb_data("search/person?query=%s&include_adult=%s&" % (url_quote(persons[0]), include_adult), 30)
    if response and "results" in response:
        if len(response["results"]) > 1 and not skip_dialog:
            listitems = create_listitems(handle_tmdb_people(response["results"]))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            w = SelectDialog('DialogSelect.xml', ADDON_PATH, listing=listitems)
            w.doModal()
            if w.index >= 0:
                return response["results"][w.index]
        elif response["results"]:
            return response["results"][0]
    else:
        log("could not find Person ID")
    return False


def get_keyword_id(keyword):
    response = get_tmdb_data("search/keyword?query=%s&include_adult=%s&" % (url_quote(keyword), include_adult), 30)
    if response and "results" in response and response["results"]:
        if len(response["results"]) > 1:
            names = [item["name"] for item in response["results"]]
            selection = xbmcgui.Dialog().select(ADDON.getLocalizedString(32114), names)
            if selection > -1:
                return response["results"][selection]
        elif response["results"]:
            return response["results"][0]
    else:
        log("could not find Keyword ID")
        return False


def get_set_id(set_name):
    set_name = set_name.replace("[", "").replace("]", "").replace("Kollektion", "Collection")
    response = get_tmdb_data("search/collection?query=%s&language=%s&" % (url_quote(set_name.encode("utf-8")), ADDON.getSetting("LanguageID")), 14)
    if "results" in response and response["results"]:
        return response["results"][0]["id"]
    else:
        return ""


def get_tmdb_data(url="", cache_days=14, folder="TheMovieDB"):
    # session_id = get_session_id()
    # url = URL_BASE + "%sapi_key=%s&session_id=%s" % (url, TMDB_KEY, session_id)
    url = URL_BASE + "%sapi_key=%s" % (url, TMDB_KEY)
    global base_url
    global poster_size
    global fanart_size
    if not base_url:
        base_url = True
        base_url, poster_size, fanart_size = get_tmdb_config()
    return get_JSON_response(url, cache_days, folder)


def get_tmdb_config():
    return ("http://image.tmdb.org/t/p/", "w500", "w1280")
    response = get_tmdb_data("configuration?", 60)
    if response:
        return (response["images"]["base_url"], response["images"]["POSTER_SIZES"][-2], response["images"]["BACKDROP_SIZES"][-2])
    else:
        return ("", "", "")


def get_company_data(company_id):
    response = get_tmdb_data("company/%s/movies?append_to_response=movies&" % (company_id), 30)
    if response and "results" in response:
        return handle_tmdb_movies(response["results"])
    else:
        return []


def get_credit_info(credit_id):
    response = get_tmdb_data("credit/%s?language=%s&" % (str(credit_id), ADDON.getSetting("LanguageID")), 30)
    prettyprint(response)
    return response
    # if response and "results" in response:
    #     return handle_tmdb_movies(response["results"])
    # else:
    #     return []


def get_image_urls(poster=None, still=None, fanart=None, profile=None):
    images = {}
    if poster:
        images["poster"] = base_url + "w500" + poster
        images["poster_original"] = base_url + "original" + poster
        images["poster_small"] = base_url + "w342" + poster
    if still:
        images["still"] = base_url + "w300" + still
        images["still_original"] = base_url + "original" + still
        images["still_small"] = base_url + "w185" + still
    if fanart:
        images["fanart"] = base_url + "w1280" + fanart
        images["fanart_original"] = base_url + "original" + fanart
        images["fanart_small"] = base_url + "w780" + fanart
    if profile:
        images["profile"] = base_url + "w500" + profile
        images["profile_original"] = base_url + "original" + profile
        images["profile_small"] = base_url + "w342" + profile
    return images


def extended_season_info(tmdb_tvshow_id, tvshow_name, season_number):
    if not tmdb_tvshow_id:
        response = get_tmdb_data("search/tv?query=%s&language=%s&" % (url_quote(tvshow_name), ADDON.getSetting("LanguageID")), 30)
        if response["results"]:
            tmdb_tvshow_id = str(response['results'][0]['id'])
        else:
            tvshow_name = re.sub('\(.*?\)', '', tvshow_name)
            response = get_tmdb_data("search/tv?query=%s&language=%s&" % (url_quote(tvshow_name), ADDON.getSetting("LanguageID")), 30)
            if response["results"]:
                tmdb_tvshow_id = str(response['results'][0]['id'])
    response = get_tmdb_data("tv/%s/season/%s?append_to_response=videos,images,external_ids,credits&language=%s&include_image_language=en,null,%s&" % (tmdb_tvshow_id, season_number, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID")), 7)
    # prettyprint(response)
    if not response:
        notify("Could not find season info")
        return None
    videos = []
    backdrops = []
    artwork = get_image_urls(poster=response.get("poster_path"))
    if response.get("name", False):
        title = response["name"]
    elif season_number == "0":
        title = "Specials"
    else:
        title = "Season %s" % season_number
    season = {'SeasonDescription': clean_text(response["overview"]),
              'Plot': clean_text(response["overview"]),
              'TVShowTitle': tvshow_name,
              'thumb': artwork.get("poster_small", ""),
              'Poster': artwork.get("poster", ""),
              'title': title,
              'ReleaseDate': response["air_date"],
              'AirDate': response["air_date"]}
    if "videos" in response:
        videos = handle_tmdb_videos(response["videos"]["results"])
    if "backdrops" in response["images"]:
        backdrops = handle_tmdb_images(response["images"]["backdrops"])
    answer = {"general": season,
              "actors": handle_tmdb_people(response["credits"]["cast"]),
              "crew": handle_tmdb_people(response["credits"]["crew"]),
              "videos": videos,
              "episodes": handle_tmdb_episodes(response["episodes"]),
              "images": handle_tmdb_images(response["images"]["posters"]),
              "backdrops": backdrops}
    return answer


def get_movie_tmdb_id(imdb_id=None, name=None, dbid=None):
    if dbid and (int(dbid) > 0):
        movie_id = get_imdb_id_from_db("movie", dbid)
        log("IMDB Id from local DB:" + str(movie_id))
        return movie_id
    elif imdb_id:
        response = get_tmdb_data("find/tt%s?external_source=imdb_id&language=%s&" % (imdb_id.replace("tt", ""), ADDON.getSetting("LanguageID")), 30)
        return response["movie_results"][0]["id"]
    elif name:
        return search_media(name)
    else:
        return None


def get_show_tmdb_id(tvdb_id=None, source="tvdb_id"):
    response = get_tmdb_data("find/%s?external_source=%s&language=%s&" % (tvdb_id, source, ADDON.getSetting("LanguageID")), 30)
    try:
        return response["tv_results"][0]["id"]
    except:
        notify("TVShow Info not available.")
        return None


def get_trailer(movie_id=None):
    response = get_tmdb_data("movie/%s?append_to_response=account_states,alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&include_image_language=en,null,%s&language=%s&" %
                             (movie_id, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID")), 30)
    if response and "videos" in response and response['videos']['results']:
        return response['videos']['results'][0]['key']
    notify("Could not get trailer")
    return ""


def extended_movie_info(movie_id=None, dbid=None, cache_time=14):
    if check_login():
        session_string = "session_id=%s&" % (get_session_id())
    else:
        session_string = ""
    response = get_tmdb_data("movie/%s?append_to_response=account_states,alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&include_image_language=en,null,%s&language=%s&%s" %
                             (movie_id, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID"), session_string), cache_time)
    if not response:
        notify("Could not get movie information")
        return {}
    mpaa = ""
    set_name = ""
    set_id = ""
    genres = [item["name"] for item in response["genres"]]
    Studio = [item["name"] for item in response["production_companies"]]
    authors = [item["name"] for item in response['credits']['crew'] if item["job"] == "Author"]
    directors = [item["name"] for item in response['credits']['crew'] if item["job"] == "Director"]
    if response['releases']['countries']:
        mpaa = response['releases']['countries'][0]['certification']
    movie_set = fetch(response, "belongs_to_collection")
    if movie_set:
        set_name = fetch(movie_set, "name")
        set_id = fetch(movie_set, "id")
    artwork = get_image_urls(poster=response.get("poster_path"), fanart=response.get("backdrop_path"))
    path = 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % str(fetch(response, "id"))
    movie = {'Art(fanart)': artwork.get("fanart", ""),
             'Art(poster)': artwork.get("poster", ""),
             'thumb': artwork.get("poster_small", ""),
             'Poster': artwork.get("poster", ""),
             'fanart': artwork.get("fanart", ""),
             'title': fetch(response, 'title'),
             'Label': fetch(response, 'title'),
             'Tagline': fetch(response, 'tagline'),
             'duration': fetch(response, 'runtime'),
             'duration(h)': format_time(fetch(response, 'runtime'), "h"),
             'duration(m)': format_time(fetch(response, 'runtime'), "m"),
             'mpaa': mpaa,
             'Director': " / ".join(directors),
             'Writer': " / ".join(authors),
             'Budget': millify(fetch(response, 'budget')),
             'Revenue': millify(fetch(response, 'revenue')),
             'Homepage': fetch(response, 'homepage'),
             'Set': set_name,
             'SetId': set_id,
             'id': fetch(response, 'id'),
             'imdb_id': fetch(response, 'imdb_id'),
             'Plot': clean_text(fetch(response, 'overview')),
             'OriginalTitle': fetch(response, 'original_title'),
             'Country': fetch(response, 'original_language'),
             'Genre': " / ".join(genres),
             'Rating': fetch(response, 'vote_average'),
             'Votes': fetch(response, 'vote_count'),
             'Adult': str(fetch(response, 'adult')),
             'Popularity': fetch(response, 'popularity'),
             'Status': fetch(response, 'status'),
             'path': path,
             'ReleaseDate': fetch(response, 'release_date'),
             'Premiered': fetch(response, 'release_date'),
             'Studio': " / ".join(Studio),
             'year': get_year(fetch(response, 'release_date'))}
    if "videos" in response:
        videos = handle_tmdb_videos(response["videos"]["results"])
    else:
        videos = []
    if "account_states" in response:
        account_states = response["account_states"]
    else:
        account_states = None
    if dbid:
        local_item = get_movie_from_db(dbid)
        movie.update(local_item)
    else:
        movie = merge_with_local_movie_info([movie])[0]
    if movie:
        answer = {"general": movie,
                  "actors": handle_tmdb_people(response["credits"]["cast"]),
                  "similar": handle_tmdb_movies(response["similar"]["results"]),
                  "lists": handle_tmdb_misc(response["lists"]["results"]),
                  "studios": handle_tmdb_misc(response["production_companies"]),
                  "releases": handle_tmdb_misc(response["releases"]["countries"]),
                  "crew": handle_tmdb_people(response["credits"]["crew"]),
                  "genres": handle_tmdb_misc(response["genres"]),
                  "keywords": handle_tmdb_misc(response["keywords"]["keywords"]),
                  "reviews": handle_tmdb_misc(response["reviews"]["results"]),
                  "videos": videos,
                  "account_states": account_states,
                  "images": handle_tmdb_images(response["images"]["posters"]),
                  "backdrops": handle_tmdb_images(response["images"]["backdrops"])}
    else:
        answer = []
    return answer


def extended_tvshow_info(tvshow_id=None, cache_time=7, dbid=None):
    session_string = ""
    if check_login():
        session_string = "session_id=%s&" % (get_session_id())
    response = get_tmdb_data("tv/%s?append_to_response=account_states,alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s" %
                             (str(tvshow_id), ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID"), session_string), cache_time)
    if not response:
        return False
    videos = []
    if "account_states" in response:
        account_states = response["account_states"]
    else:
        account_states = None
    if "videos" in response:
        videos = handle_tmdb_videos(response["videos"]["results"])
    tmdb_id = fetch(response, 'id')
    artwork = get_image_urls(poster=response.get("poster_path"), fanart=response.get("backdrop_path"))
    if len(response.get("episode_run_time", -1)) > 1:
        duration = "%i - %i" % (min(response["episode_run_time"]), max(response["episode_run_time"]))
    elif len(response.get("episode_run_time", -1)) == 1:
        duration = "%i" % (response["episode_run_time"][0])
    else:
        duration = ""
    genres = [item["name"] for item in response["genres"]]
    tvshow = {'Art(fanart)': artwork.get("fanart", ""),
              'Art(poster)': artwork.get("poster", ""),
              'thumb': artwork.get("poster", ""),
              'Poster': artwork.get("poster", ""),
              'fanart': artwork.get("fanart", ""),
              'title': fetch(response, 'name'),
              'TVShowTitle': fetch(response, 'name'),
              'OriginalTitle': fetch(response, 'original_name'),
              'duration': duration,
              'duration(h)': format_time(duration, "h"),
              'duration(m)': format_time(duration, "m"),
              'id': tmdb_id,
              'Genre': " / ".join(genres),
              'credit_id': fetch(response, 'credit_id'),
              'Plot': clean_text(fetch(response, "overview")),
              'year': get_year(fetch(response, 'first_air_date')),
              'media_type': "tv",
              'path': 'plugin://script.extendedinfo/?info=action&&id=RunScript(script.extendedinfo,info=extendedtvinfo,id=%s)' % tmdb_id,
              'Rating': fetch(response, 'vote_average'),
              'User_Rating': str(fetch(response, 'rating')),
              'Votes': fetch(response, 'vote_count'),
              'Status': fetch(response, 'status'),
              'ShowType': fetch(response, 'type'),
              'homepage': fetch(response, 'homepage'),
              'last_air_date': fetch(response, 'last_air_date'),
              'first_air_date': fetch(response, 'first_air_date'),
              'number_of_episodes': fetch(response, 'number_of_episodes'),
              'number_of_seasons': fetch(response, 'number_of_seasons'),
              'in_production': fetch(response, 'in_production'),
              'Release_Date': fetch(response, 'first_air_date'),
              'ReleaseDate': fetch(response, 'first_air_date'),
              'Premiered': fetch(response, 'first_air_date')}
    if dbid:
        local_item = get_tvshow_from_db(dbid)
        tvshow.update(local_item)
    else:
        tvshow = merge_with_local_tvshow_info([tvshow])[0]
    answer = {"general": tvshow,
              "actors": handle_tmdb_people(response["credits"]["cast"]),
              "similar": handle_tmdb_tvshows(response["similar"]["results"]),
              "studios": handle_tmdb_misc(response["production_companies"]),
              "networks": handle_tmdb_misc(response["networks"]),
              "certifications": handle_tmdb_misc(response["content_ratings"]["results"]),
              "crew": handle_tmdb_people(response["credits"]["crew"]),
              "genres": handle_tmdb_misc(response["genres"]),
              "keywords": handle_tmdb_misc(response["keywords"]["results"]),
              "videos": videos,
              "account_states": account_states,
              "seasons": handle_tmdb_seasons(response["seasons"]),
              "images": handle_tmdb_images(response["images"]["posters"]),
              "backdrops": handle_tmdb_images(response["images"]["backdrops"])}
    return answer


def extended_episode_info(tvshow_id, season, episode, cache_time=7):
    if not season:
        season = 0
    session_string = ""
    if check_login():
        session_string = "session_id=%s&" % (get_session_id())
    response = get_tmdb_data("tv/%s/season/%s/episode/%s?append_to_response=account_states,credits,external_ids,images,rating,videos&language=%s&include_image_language=en,null,%s&%s&" %
                             (str(tvshow_id), str(season), str(episode), ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID"), session_string), cache_time)
    videos = []
    # prettyprint(response)
    if "videos" in response:
        videos = handle_tmdb_videos(response["videos"]["results"])
    if "account_states" in response:
        account_states = response["account_states"]
    else:
        account_states = None
    answer = {"general": handle_tmdb_episodes([response])[0],
              "actors": handle_tmdb_people(response["credits"]["cast"]),
              "account_states": account_states,
              "crew": handle_tmdb_people(response["credits"]["crew"]),
              "guest_stars": handle_tmdb_people(response["credits"]["guest_stars"]),
              # "genres": handle_tmdb_misc(response["genres"]),
              "videos": videos,
              # "seasons": handle_tmdb_seasons(response["seasons"]),
              "images": handle_tmdb_images(response["images"]["stills"])}
    return answer


def extended_actor_info(actor_id):
    response = get_tmdb_data("person/%s?append_to_response=tv_credits,movie_credits,combined_credits,images,tagged_images&" % (actor_id), 1)
    tagged_images = []
    if "tagged_images" in response:
        tagged_images = handle_tmdb_tagged_images(response["tagged_images"]["results"])
    answer = {"general": handle_tmdb_people([response])[0],
              "movie_roles": handle_tmdb_movies(response["movie_credits"]["cast"]),
              "tvshow_roles": handle_tmdb_tvshows(response["tv_credits"]["cast"]),
              "movie_crew_roles": handle_tmdb_movies(response["movie_credits"]["crew"]),
              "tvshow_crew_roles": handle_tmdb_tvshows(response["tv_credits"]["crew"]),
              "tagged_images": tagged_images,
              "images": handle_tmdb_images(response["images"]["profiles"])}
    return answer


def get_movie_lists(list_id):
    response = get_tmdb_data("movie/%s?append_to_response=account_states,alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&include_image_language=en,null,%s&language=%s&" %
                             (list_id, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID")), 5)
    return handle_tmdb_misc(response["lists"]["results"])


def get_rated_media_items(media_type):
    '''takes "tv/episodes", "tv" or "movies"'''
    if check_login():
        session_id = get_session_id()
        account_id = get_account_info()
        if not session_id:
            notify("Could not get session id")
            return []
        response = get_tmdb_data("account/%s/rated/%s?session_id=%s&language=%s&" % (str(account_id), media_type, session_id, ADDON.getSetting("LanguageID")), 0)
    else:
        session_id = get_guest_session_id()
        if not session_id:
            notify("Could not get session id")
            return []
        response = get_tmdb_data("guest_session/%s/rated_movies?language=%s&" % (session_id, ADDON.getSetting("LanguageID")), 0)
    if media_type == "tv/episodes":
        return handle_tmdb_episodes(response["results"])
    elif media_type == "tv":
        return handle_tmdb_tvshows(response["results"], False, None)
    else:
        return handle_tmdb_movies(response["results"], False, None)


def get_fav_items(media_type):
    '''takes "tv/episodes", "tv" or "movies"'''
    session_id = get_session_id()
    account_id = get_account_info()
    if not session_id:
        notify("Could not get session id")
        return []
    response = get_tmdb_data("account/%s/favorite/%s?session_id=%s&language=%s&" % (str(account_id), media_type, session_id, ADDON.getSetting("LanguageID")), 0)
    if "results" in response:
        if media_type == "tv":
            return handle_tmdb_tvshows(response["results"], False, None)
        elif media_type == "tv/episodes":
            return handle_tmdb_episodes(response["results"])
        else:
            return handle_tmdb_movies(response["results"], False, None)
    else:
        return []


def get_movies_from_list(list_id, cache_time=5):
    '''
    get movie dict list from tmdb list.
    '''

    response = get_tmdb_data("list/%s?language=%s&" % (str(list_id), ADDON.getSetting("LanguageID")), cache_time)
    return handle_tmdb_movies(response["items"], False, None)


def get_popular_actors():
    '''
    get dict list containing popular actors / directors / writers
    '''
    response = get_tmdb_data("person/popular?", 1)
    return handle_tmdb_people(response["results"])


def get_actor_credits(actor_id, media_type):
    '''
    media_type: movie or tv
    '''
    response = get_tmdb_data("person/%s/%s_credits?" % (actor_id, media_type), 1)
    return handle_tmdb_movies(response["cast"])


def get_keywords(movie_id):
    '''
    get dict list containing movie keywords
    '''
    response = get_tmdb_data("movie/%s?append_to_response=account_states,alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&include_image_language=en,null,%s&language=%s&" %
                             (movie_id, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID")), 30)
    keywords = []
    if "keywords" in response:
        for keyword in response["keywords"]["keywords"]:
            keyword_dict = {'id': fetch(keyword, 'id'),
                            'name': keyword['name']}
            keywords.append(keyword_dict)
    return keywords


def get_similar_movies(movie_id):
    '''
    get dict list containing movies similar to *movie_id
    '''

    response = get_tmdb_data("movie/%s?append_to_response=account_states,alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&include_image_language=en,null,%s&language=%s&" %
                             (movie_id, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID")), 10)
    if "similar" in response:
        return handle_tmdb_movies(response["similar"]["results"])
    else:
        log("No JSON Data available")
        return []


def get_similar_tvshows(tvshow_id):
    '''
    return list with similar tvshows for show with *tvshow_id (TMDB ID)
    '''
    session_string = ""
    if check_login():
        session_string = "session_id=%s&" % (get_session_id())
    response = get_tmdb_data("tv/%s?append_to_response=account_states,alternative_titles,content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&include_image_language=en,null,%s&%s" %
                             (str(tvshow_id), ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID"), session_string), 10)
    if "similar" in response:
        return handle_tmdb_tvshows(response["similar"]["results"])
    else:
        log("No JSON Data available")
        return []


def get_tmdb_shows(tvshow_type):
    '''
    return list with tv shows
    available types: airing, on_the_air, top_rated, popular
    '''
    response = get_tmdb_data("tv/%s?language=%s&" % (tvshow_type, ADDON.getSetting("LanguageID")), 0.3)
    if "results" in response:
        return handle_tmdb_tvshows(response["results"], False, None)
    else:
        log("No JSON Data available for get_tmdb_shows(%s)" % tvshow_type)
        log(response)
        return []


def get_tmdb_movies(movie_type):
    '''
    return list with movies
    available types: now_playing, upcoming, top_rated, popular
    '''
    response = get_tmdb_data("movie/%s?language=%s&" % (movie_type, ADDON.getSetting("LanguageID")), 0.3)
    if "results" in response:
        return handle_tmdb_movies(response["results"], False, None)
    else:
        log("No JSON Data available for get_tmdb_movies(%s)" % movie_type)
        log(response)
        return []


def get_set_movies(set_id):
    '''
    return list with movies which are part of set with *set_id
    '''
    response = get_tmdb_data("collection/%s?language=%s&append_to_response=images&include_image_language=en,null,%s&" % (set_id, ADDON.getSetting("LanguageID"), ADDON.getSetting("LanguageID")), 14)
    if response:
        artwork = get_image_urls(poster=response.get("poster_path"), fanart=response.get("backdrop_path"))
        info = {"label": response["name"],
                "Poster": artwork.get("poster", ""),
                "thumb": artwork.get("poster_small", ""),
                "Fanart": artwork.get("fanart", ""),
                "overview": response["overview"],
                "id": response["id"]}
        return handle_tmdb_movies(response.get("parts", [])), info
    else:
        log("No JSON Data available")
        return [], {}


def get_person_movies(person_id):
    response = get_tmdb_data("person/%s/credits?language=%s&" % (person_id, ADDON.getSetting("LanguageID")), 14)
    # return handle_tmdb_movies(response["crew"]) + handle_tmdb_movies(response["cast"])
    if "crew" in response:
        return handle_tmdb_movies(response["crew"])
    else:
        log("No JSON Data available")
        return []


def search_media(media_name=None, year='', media_type="movie"):
    '''
    return list of items with type *media_type for search with *media_name
    '''
    search_query = url_quote(media_name + " " + str(year))
    if search_query:
        response = get_tmdb_data("search/%s?query=%s&language=%s&include_adult=%s&" % (media_type, search_query, ADDON.getSetting("LanguageID"), include_adult), 1)
        try:
            if not response == "Empty":
                for item in response['results']:
                    if item['id']:
                        return item['id']
        except Exception as e:
            log(e)
    return None


class GetYoutubeVidsThread(threading.Thread):

    def __init__(self, search_string="", hd="", order="relevance", limit=15):
        threading.Thread.__init__(self)
        self.search_string = search_string
        self.hd = hd
        self.order = order
        self.limit = limit

    def run(self):
        self.listitems = get_youtube_search_videos(self.search_string, self.hd, self.order, self.limit)
