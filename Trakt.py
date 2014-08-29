import xbmcvfs, datetime, time, os, sys
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

trakt_key = '7b2281f0d441ab1bf4fdc39fd6cccf15'


def GetTraktCalendarShows(Type):
    shows = []
    results = ""
    url = 'http://api.trakt.tv/calendar/%s.json/%s/today/14' % (Type,trakt_key)
    try:
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching Trakt data from net")
        log("Json Query: " + url)
    count = 1
    if results:
        for day in results:
            for episode in day["episodes"]:
                show = {'Title' : episode["episode"]["title"],
                        'TVShowTitle' : episode["show"]["title"],
                        'ID' : episode["show"]["tvdb_id"],
                        'Runtime' : episode["show"]["runtime"],
                        'Year' : episode["show"].get("year"),
                        'Certification' : episode["show"]["certification"],
                        'Studio' : episode["show"]["network"],
                        'Plot' : episode["show"]["overview"],
                        'Genre' : " / ".join(episode["show"]["genres"]),
                        'Thumb' : episode["episode"]["images"]["screen"],
                        'Art(poster)' : episode["show"]["images"]["poster"],
                        'Art(banner)' : episode["show"]["images"]["banner"],
                        'Art(fanart)' : episode["show"]["images"]["fanart"]  }
                shows.append(show)
                count += 1
                if count > 20:
                    break
    return shows

def HandleTraktMovieResult(results):
    count = 1
    movies = []
    for movie in results:   
        try:
            premiered = str(datetime.datetime.fromtimestamp(int(movie["released"])))[:10]
        except:
            premiered = ""
        try:         
            movie = {'Title': movie["title"],
                    'Runtime': movie["runtime"],
                    'Tagline': movie["tagline"],
                    'Trailer': ConvertYoutubeURL(movie["trailer"]),
                    'Year': movie["year"],
                    'ID': movie["tmdb_id"],
                    'mpaa': movie["certification"],
                    'Plot': movie["overview"],
                    'Premiered': premiered,
                    'Rating': movie["ratings"]["percentage"]/10.0,
                    'Votes': movie["ratings"]["votes"],
                    'Watchers': movie["watchers"],
                    'Genre': " / ".join(movie["genres"]),
                    'Art(poster)': movie["images"]["poster"],
                    'Art(fanart)': movie["images"]["fanart"]  }
            movies.append(movie)
        except Exception,e:
            log(e)          
        count += 1
        if count > 20:
            break
    return movies

def HandleTraktTVShowResult(results):
    count = 1
    shows = []
    for tvshow in results:    
        try:
            premiered = str(datetime.datetime.fromtimestamp(int(tvshow["first_aired"])))[:10]
        except:
            premiered = ""
        show = {'Title': tvshow["title"],
                'Label': tvshow["title"],
                'TVShowTitle': tvshow["title"],
                'Runtime': tvshow["runtime"],
                'Year': tvshow["year"],
                'Status': tvshow["status"],
                'mpaa': tvshow["certification"],
                'Studio': tvshow["network"],
                'Plot': tvshow["overview"],
                'ID': tvshow["tvdb_id"],
                'AirDay': tvshow["air_day"],
                'AirShortTime': tvshow["air_time"],
                'Label2': tvshow["air_day"] + " " + tvshow["air_time"],
                'Premiered': premiered,
                'Country': tvshow["country"],
                'Rating': tvshow["ratings"]["percentage"]/10.0,
                'Votes': tvshow["ratings"]["votes"],
                'Watchers': tvshow["watchers"],
                'Genre': " / ".join(tvshow["genres"]),
                'Art(poster)': tvshow["images"]["poster"],
                'Poster': tvshow["images"]["poster"],
                'Art(banner)': tvshow["images"]["banner"],
                'Art(fanart)': tvshow["images"]["fanart"],
                'Fanart': tvshow["images"]["fanart"],
                'Thumb': tvshow["images"]["fanart"]  }
        shows.append(show)
        count += 1
        if count > 20:
            break
    return shows
    
def GetTrendingShows():
    results = ""
    filename = Addon_Data_Path + "/trendingshows.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        return HandleTraktTVShowResult(results)
    else:    
        url = 'http://api.trakt.tv/shows/trending.json/%s' % trakt_key
        try:
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
            save_to_file(results,"trendingshows",Addon_Data_Path)
        except Exception, e:
            log("Error when fetching  trending data from Trakt.tv")
            log(e)
            log(url)
        if results:
            return HandleTraktTVShowResult(results)
            
def GetTVShowInfo(id):
    results = ""
    filename = Addon_Data_Path + "/tvshow" + id + ".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        return HandleTraktTVShowResult([results])
    else:    
        url = 'http://api.trakt.tv/show/summary.json/%s/%s' % (trakt_key,id)
        try:
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
            save_to_file(results,"tvshow" + id,Addon_Data_Path)
        except Exception, e:
            log("Error when fetching  trending data from Trakt.tv (GetTVShowInfo)")
            log(e)
            log(url)
        if results:
            return HandleTraktTVShowResult([results])
                       
    
def GetTrendingMovies():
    results = ""
    filename = Addon_Data_Path + "/trendingmovies.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
   #     log(results)
        return HandleTraktMovieResult(results)
    else:  
        url = 'http://api.trakt.tv/movies/trending.json/%s' % trakt_key
        try:
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
        except Exception, e:
            log("Error when fetching  trending data from Trakt.tv (GetTrendingMovies). URL and exception:")
            log(url)
            log(e)
        count = 1
        if results:
            return HandleTraktMovieResult(results)
       
def GetSimilarTrakt(type,imdb_id):
    movies = []
    shows = []
    results = ""
    if type == "tvshow":
        type = "show"
    filename = Addon_Data_Path + "/similar" + type + imdb_id + ".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 1:
        results = read_from_file(filename)
        if type == "show":
            return HandleTraktTVShowResult(results)
        elif type =="movie":
            return HandleTraktMovieResult(results)
    else:         
        url = 'http://api.trakt.tv/%s/related.json/%s/%s/' % (type, trakt_key, imdb_id)
        try:
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
            save_to_file(results,"similar" + type + imdb_id,Addon_Data_Path)
        except:
            log("Error when fetching  trending data from Trakt.tv")
            log(url)
        if results:
            if type == "show":
                return HandleTraktTVShowResult(results)
            elif type =="movie":
                return HandleTraktMovieResult(results)
    return[]