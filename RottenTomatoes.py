from Utils import *
import sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

rottentomatoes_key = '63sbsudx936yedd2wdmt6tkn'
base_url = "http://api.rottentomatoes.com/api/public/v1.0/lists/"


def GetRottenTomatoesMoviesInTheaters(type):
    movies = []
    try:
        url = 'movies/in_theaters.json?apikey=%s' % (rottentomatoes_key)
        results = Get_JSON_response(base_url, url)
    except:
        results = None
        Notify("Error when fetching RottenTomatoes data from net")
    count = 1
    if results is not None:
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"] / 10.0,
                     'Plot': item["synopsis"]}
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies


def GetRottenTomatoesMoviesOpening(type):
    movies = []
    try:
        url = 'movies/opening.json?apikey=%s' % (rottentomatoes_key)
        results = Get_JSON_response(base_url, url)
    except:
        results = None
        Notify("Error when fetching RottenTomatoes data from net")
    count = 1
    if results is not None:
 #       log(results)
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"] / 10.0,
                     'Plot': item["synopsis"]}
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies


def GetRottenTomatoesMoviesComingSoon(type):
    movies = []
    try:
        url = 'movies/upcoming.json?apikey=%s' % (rottentomatoes_key)
        results = Get_JSON_response(base_url, url)
    except:
        Notify("Error when fetching RottenTomatoes data from net")
        results = None
    count = 1
    if results is not None:
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"] / 10.0,
                     'Plot': item["synopsis"]}
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies


def GetRottenTomatoesMoviesBoxOffice(type):
    movies = []
    try:
        url = 'movies/box_office.json?apikey=%s' % (rottentomatoes_key)
        results = Get_JSON_response(base_url, url)
    except:
        Notify("Error when fetching RottenTomatoes data from net")
        results = None
    count = 1
    if results is not None:
    #    log(results)
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"] / 10.0,
                     'Plot': item["synopsis"]}
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies
