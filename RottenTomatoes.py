from Utils import GetStringFromUrl
import sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

rottentomatoes_key = 'sr9ambpra5r3ys2khtxn5bxt'


def GetRottenTomatoesMoviesInTheaters(type):
    movies = []
    results = ""
    try:
        url = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/in_theaters.json?apikey=%s' % (rottentomatoes_key)
        log("Json Query: " + url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching RottenTomatoes data from net")
    count = 1
    if results:
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"]/10.0,
                     'Plot': item["synopsis"]  }
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies

def GetRottenTomatoesMoviesOpening(type):
    movies = []
    results = ""
    try:
        url = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/opening.json?apikey=%s' % (rottentomatoes_key)
        log("Json Query: " + url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching RottenTomatoes data from net")
    count = 1
    if results:
 #       log(results)
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"]/10.0,
                     'Plot': item["synopsis"]  }
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies
    
def GetRottenTomatoesMoviesComingSoon(type):
    movies = []
    results = ""
    try:
        url = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/upcoming.json?apikey=%s' % (rottentomatoes_key)
        log("Json Query: " + url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching RottenTomatoes data from net")
    count = 1
    if results:
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"]/10.0,
                     'Plot': item["synopsis"]  }
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies

def GetRottenTomatoesMoviesBoxOffice(type):
    movies = []
    results = ""
    try:
        url = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/box_office.json?apikey=%s' % (rottentomatoes_key)
        log("Json Query: " + url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching RottenTomatoes data from net")
    count = 1
    if results:
    #    log(results)
        for item in results["movies"]:
            movie = {'Title': item["title"],
                     'Art(poster)': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'Premiered': item["release_dates"]["theater"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["audience_score"]/10.0,
                     'Plot': item["synopsis"]  }
            movies.append(movie)
            count += 1
            if count > 20:
                break
    return movies