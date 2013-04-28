import xbmcaddon, os, xbmc, xbmcvfs, time
import simplejson as json
from Utils import log, prettyprint, read_from_file, save_to_file, CompareWithLibrary
import urllib
from urllib2 import Request, urlopen

moviedb_key = '34142515d9d23817496eeb4ff1d223d0'
__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__language__     = __addon__.getLocalizedString   
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % __addonid__ ).decode("utf-8") )
base_url = ""
poster_size = ""
fanart_size = ""

def HandleTheMovieDBMovieResult(results):
    movies = []
    log("starting HandleTheMovieDBMovieResult")
    if True:
        for movie in results:
            log(movie)
            newmovie = {'Art(fanart)': base_url + fanart_size + str(movie.get('backdrop_path',"")),
                        'Art(poster)': base_url + poster_size + str(movie.get('poster_path',"")),
                        'Title': movie.get('title',""),
                        'OriginalTitle': movie.get('original_title',""),
                        'ID': movie.get('id',""),
                        'Path': "",
                        'Play': "",
                        'DBID': "",
                        'Rating': movie.get('vote_average',""),
                        'Premiered':movie.get('release_date',"")  }
            if not str(movie['id']) in str(movies): ## too dirty
                movies.append(newmovie)
    else:
        log("Error when handling TheMovieDB movie results")
    movies = CompareWithLibrary(movies)        
    return movies
    
def HandleTheMovieDBListResult(results):
    lists = []
    if True:
        for list in results["lists"]["results"]:
            newlist = {'Art(poster)': base_url + poster_size + str(list.get('poster_path',"")),
                        'Title': list['name'],
                        'ID': list['id'],
                        'Description': list['description']}
            lists.append(newlist)
    else:
        pass
    return lists
    
def HandleTheMovieDBPeopleResult(results):
    people = []
    if True:
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
    else:
        log("Error when handling TheMovieDB people results")
    return people
    
def HandleTheMovieDBCompanyResult(results):
    companies = []
    log("starting HandleLastFMCompanyResult")
    if True:
        for company in results:
            newcompany = {'parent_company': company['parent_company'],
                        'name': company['name'],
                        'description': company['description'],
                        'headquarters': company['headquarters'],
                        'homepage': company['homepage'],
                        'id': company['id'],
                        'logo_path': company['logo_path'] }
            companies.append(newcompany)
    else:
        log("Error when handling TheMovieDB companies results")
    return companies
    
def SearchforCompany(Company):
  #  Companies = Company.split(" / ")
   # Company = Companies[0]
    import re
    regex = re.compile('\(.+?\)')
    Company = regex.sub('', Company)
    log(Company)
    response = GetMovieDBData("search/company?query=%s&" % urllib.quote_plus(Company),30)
    try:
        return response["results"][0]["id"]
    except:
        log("could not find Company ID")
        return ""
        
def GetPersonID(person):
    Persons = person.split(" / ")
    person = Persons[0]
    response = GetMovieDBData("search/person?query=%s&" % urllib.quote_plus(person),30)
    try:
        return response["results"][0]["id"]
    except:
        log("could not find Person ID")
        return ""
        
def SearchForSet(setname):
    setname = setname.replace("[","").replace("]","").replace("Kollektion","Collection")
    response = GetMovieDBData("search/collection?query=%s&language=%s&" % (urllib.quote_plus(setname.encode("utf-8")), __addon__.getSetting("LanguageID")),14)
    try:
        return response["results"][0]["id"]
    except:
        return ""

def GetMovieDBData(url = "", cache_days = 14):
    from base64 import b64encode
    global base_url
    global poster_size
    global fanart_size
    if not base_url:
        log("fetching base_url and size (MovieDB config)")
        base_url = True
        base_url, poster_size, fanart_size = GetMovieDBConfig()
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    log("trying to load "  + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = "http://api.themoviedb.org/3/" + url + "api_key=%s" % moviedb_key
        log("Downloading MovieDB Data: " + url)
        headers = {"Accept": "application/json"}
        succeed = 0
        while succeed < 3:
            try:
                request = Request(url, headers = headers)
                response = urlopen(request).read()
                log(response)
                log("saved file " + filename)
                response = json.loads(response)
                save_to_file(response,filename,Addon_Data_Path)
                return response
            except:
                log("could not get data from %s" % url)
                xbmc.sleep(1000)
                succeed += 1
        return []

        
def GetMovieDBConfig():
    response = GetMovieDBData("configuration?",60)
    if response:
        return (response["images"]["base_url"],response["images"]["poster_sizes"][-2],response["images"]["backdrop_sizes"][-2])
    else:
        return ("","")
    
def GetCompanyInfo(Id):
    response = GetMovieDBData("company/%s/movies?append_to_response=movies&" % (Id),30)
    if response and "results" in response:
        return HandleTheMovieDBMovieResult(response["results"])
    else:
        return []
    
def GetExtendedMovieInfo(Id):
    response = GetMovieDBData("movie/%s?append_to_response=trailers,casts,releases,keywords,similar_movies,lists&language=%s&" % (Id, __addon__.getSetting("LanguageID")),30)
    prettyprint(response)
    if True:
        authors = []
        directors = []
        genres = []
        for item in response['genres']:
            genres.append(item["name"])
        for item in response['casts']['crew']:
            if item["job"] == "Author":
                authors.append(item["name"])
            if item["job"] == "Director":
                directors.append(item["name"])
        Writer = " / ".join(authors)
        Director = " / ".join(directors)
        Genre = " / ".join(genres)
        if len(response['trailers']['youtube']) > 0:
            Trailer = response['trailers']['youtube'][0]['source']
        else:
            Trailer = ""
        if len(response['releases']['countries']) > 0:
            mpaa = response['releases']['countries'][0]['certification']
        else:
            mpaa = ""
        if len(response['production_countries']) > 0:
            Country = response['production_countries'][0]["name"]
        else:
            Country = ""
        if len(response['production_companies']) > 0:
            Studio = response['production_companies'][0]["name"]
        else:
            Studio = ""
        Set = response.get("belongs_to_collection","")
        if Set:
            SetName = Set.get("name","")
            SetID = Set.get("id","")         
        else:
            SetName = ""
            SetID = ""
        if 'release_date' in response:
            year = response.get('release_date',"")[:4]
        else:
            year = ""
        newmovie = {'Art(fanart)': base_url + fanart_size + str(response.get('backdrop_path',"")),
                    'Fanart': base_url + fanart_size + str(response.get('backdrop_path',"")),
                    'Art(poster)': base_url + poster_size + str(response.get('poster_path',"")),
                    'Poster': base_url + poster_size + str(response.get('poster_path',"")),
                    'Title': response.get('title',""),
                    'Label': response.get('title',""),
                    'Tagline': response.get('tagline',""),
                    'RunningTime': response.get('runtime',""),
                    'Budget': response.get('budget',""),
                    'mpaa': mpaa,
                    'Director': Director,
                    'Writer': Writer,
                    'Budget': response.get('budget',""),
                    'Homepage': response.get('homepage',""),
                    'Set': SetName,
                    'SetId': SetID,
                    'ID': response.get('id',""),
                    'Plot': response.get('overview',""),
                    'OriginalTitle': response.get('original_title',""),
                    'Genre': Genre,
                    'Rating': response.get('vote_average',""),
                    'Play': '',
                    'Trailer': 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' %Trailer,
                    'ReleaseDate':response.get('release_date',""),
                    'Premiered':response.get('release_date',""),
                    'Country':Country,
                    'Studio':Studio,
                    'DiscArt':"",
                    'VideoResolution':"",
                    'AudioChannels':"",
                    'VideoCodec':"",
                    'VideoAspect':"",
                    'Logo': "",
                    'DBID': "",
                    'Studio':Studio,
                    'Year': year  }
    else:
        return False
    newmovie = CompareWithLibrary([newmovie])        
    return newmovie[0]
     
def GetMovieLists(Id):
    response = GetMovieDBData("movie/%s?append_to_response=trailers,casts,releases,keywords,similar_movies,lists&language=%s&" % (Id, __addon__.getSetting("LanguageID")),30)
    return HandleTheMovieDBListResult(response)
    
def GetMovieKeywords(Id):
    response = GetMovieDBData("movie/%s?append_to_response=trailers,casts,releases,keywords,similar_movies,lists&language=%s&" % (Id, __addon__.getSetting("LanguageID")),30)
    keywords = []
    if True:
        for keyword in response["keywords"]["keywords"]:
            newkeyword = {'id': keyword.get('id',""),
                        'name': keyword['name']}
            log(newkeyword)
            keywords.append(newkeyword)
    else:
        pass
    return keywords
    
def GetSimilarMovies(Id):
    response = GetMovieDBData("movie/%s?append_to_response=trailers,casts,releases,keywords,similar_movies,lists&language=%s&" % (Id, __addon__.getSetting("LanguageID")),30)
    try:
        return HandleTheMovieDBMovieResult(response["similar_movies"]["results"])
    except:
        return []
    
def GetMovieDBMovies(type):
    response = GetMovieDBData("movie/%s?language=%s&" % ( type, __addon__.getSetting("LanguageID")),2)
    try:
        return HandleTheMovieDBMovieResult(response["results"])
    except:
        return []
        
def GetSetMovies(Id):
    response = GetMovieDBData("collection/%s?language=%s&" % (Id, __addon__.getSetting("LanguageID")),14)
    try:
        return HandleTheMovieDBMovieResult(response["parts"])
    except:
        return []
        
def GetDirectorMovies(Id):
    response = GetMovieDBData("person/%s/credits?language=%s&" % (Id, __addon__.getSetting("LanguageID")),14)
    # return HandleTheMovieDBMovieResult(response["crew"]) + HandleTheMovieDBMovieResult(response["cast"])
    try:
        return HandleTheMovieDBMovieResult(response["crew"])
    except:
        return []      
        
def search_movie(medianame,year = ''):
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame, year) )
    medianame = urllib.quote_plus(medianame.encode('utf8','ignore'))
    response = GetMovieDBData("search/movie?query=%s+%s&language=%s&" % (medianame, year, __addon__.getSetting("LanguageID")),1)
    tmdb_id = ''
    try:
        if response == "Empty":
            tmdb_id = ''
        else:
            for item in response['results']:
                if item['id']:
                    tmdb_id = item['id']
                    log(tmdb_id)
                    break
    except Exception, e:
        log( str( e ), xbmc.LOGERROR )
    if tmdb_id == '':
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found ID: %s' %tmdb_id)
    return tmdb_id
        