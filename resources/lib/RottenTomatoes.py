from Utils import *
from local_db import compare_with_library

RT_KEY = '63sbsudx936yedd2wdmt6tkn'
BASE_URL = "http://api.rottentomatoes.com/api/public/v1.0/lists/"


def GetRottenTomatoesMovies(movietype):
    movies = []
    url = movietype + '.json?apikey=%s' % (RT_KEY)
    results = Get_JSON_response(BASE_URL + url)
    if results is not None and "movies" in results:
        for item in results["movies"]:
            if "alternate_ids" in item:
                imdb_id = str(item["alternate_ids"]["imdb"])
            else:
                imdb_id = ""
            poster = "http://" + item["posters"]["original"].replace("tmb", "ori")[64:]
            if ADDON.getSetting("infodialog_onclick") != "false":
                # path = 'plugin://script.extendedinfo/?info=extendedinfo&&imdb_id=%s' % imdb_id
                path = 'plugin://script.extendedinfo/?info=action&&id=RunScript(script.extendedinfo,info=extendedinfo,imdb_id=%s)' % imdb_id
            else:
                path = "plugin://script.extendedinfo/?info=playtrailer&&imdb_id=" + imdb_id
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'imdb_id': imdb_id,
                     'Thumb': poster,
                     'Poster': poster,
                     'Runtime': item["runtime"],
                     'duration': item["runtime"],
                     'duration(h)': format_time(item["runtime"], "h"),
                     'duration(m)': format_time(item["runtime"], "m"),
                     'Year': item["year"],
                     'path': path,
                     'Premiered': item["release_dates"].get("theater", ""),
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"] / 10.0,
                     'Plot': item["synopsis"]}
            if imdb_id:
                movies.append(movie)
    movies = compare_with_library(movies, False)
    return movies
