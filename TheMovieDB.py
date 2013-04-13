import xbmcaddon,os,xbmc,xbmcvfs
import simplejson as json
from Utils import log, GetStringFromUrl, read_from_file, save_to_file
import urllib
from urllib2 import Request, urlopen

moviedb_key = '34142515d9d23817496eeb4ff1d223d0'      
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def HandleTheMovieDBMovieResult(results):
    movies = []
    log("starting HandleTheMovieDBMovieResult")
    try:
        for movie in results["movies"]["results"]:
            log(movie)
            newmovie = {'Art(fanart)': movie['backdrop_path'],
                        'Art(poster)': movie['poster_path'],
                        'Title': movie['title'],
                        'ID': movie['id'],
                        'Rating': movie['vote_average'],
                        'ReleaseDate':movie['release_date']  }
            movies.append(newmovie)
    except:
        log("Error when handling TheMovieDB movie results")
    return movies
    
def HandleTheMovieDBPeopleResult(results):
    people = []
    log("starting HandleLastFMPeopleResult")
    try:
        for person in results:
            newperson = {'adult': person['adult'],
                        'name': person['name'],
                        'also_known_as': person['also_known_as'],
                        'biography': person['biography'],
                        'birthday': person['birthday'],
                        'id': person['id'],
                        'deathday': person['deathday'],
                        'place_of_birth': person['place_of_birth'],
                        'thumb': person['profile_path']  }
            people.append(newperson)
    except:
        log("Error when handling TheMovieDB people results")
    return people
    
    
def HandleTheMovieDBCompanyResult(results):
    companies = []
    log("starting HandleLastFMCompanyResult")
    try:
        for company in results:
            log(company)
            newcompany = {'parent_company': company['parent_company'],
                        'name': company['name'],
                        'description': company['description'],
                        'headquarters': company['headquarters'],
                        'homepage': company['homepage'],
                        'id': company['id'],
                        'logo_path': company['logo_path'] }
            companies.append(newcompany)
    except:
        log("Error when handling TheMovieDB companies results")
    return companies
    
def SearchforCompany(Company):
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/search/company?query=%s&api_key=%s" % (urllib.quote_plus(Company),moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    return response["results"][0]["id"]
    
def GetCompanyInfo(Id):
    headers = {"Accept": "application/json"}
    request = Request("http://api.themoviedb.org/3/company/%s?append_to_response=movies&api_key=%s" % (Id,moviedb_key), headers=headers)
    response = urlopen(request).read()
    response = json.loads(response)
    log(response)
    return HandleTheMovieDBMovieResult(response)
    
def GetMovieDBNumber(dbid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["imdbnumber"], "movieid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = json.loads(json_query)
    if json_response['result'].has_key('moviedetails'):
        return json_response['result']['moviedetails']['imdbnumber']
    else:
        return []