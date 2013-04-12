import xbmcaddon,os,xbmc,xbmcvfs
import simplejson as json
from Utils import log, GetStringFromUrl, GetValue, read_from_file, save_to_file
import xml.dom.minidom
import urllib

bandsintown_apikey = 'xbmc_open_source_media_center'
lastfm_apikey = 'bb258101395ce46c63843bd6261e3fc8'
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def HandleBandsInTownResult(results):
    events = []
    for event in results:
        try:
            venue = event['venue']
            artists = event['artists']
            my_arts = ''
            for art in artists:
                my_arts += ' / '
                my_arts += art['name']
            my_arts = my_arts.replace(" / ", "",1)        
            event = {'date': event['datetime'].replace("T", " - ").replace(":00", "",1),
                     'city': venue['city'],
                     'name': venue['name'],
                     'region': venue['region'],
                     'country': venue['country'],
                     'artists': my_arts  }
            events.append(event)
        except: pass
    return events
    
def HandleLastFMEventResult(results):
    events = []
    log(results)
    log("starting HandleLastFMEventResult")
    try:
        for event in results['events']['event']:
            artists = event['artists']['artist']
            if isinstance(artists, list):
                my_arts = ' / '.join(artists)
            else:
                my_arts = artists
            event = {'date': event['startDate'],
                     'city': event['venue']['location']['city'],
                     'name': event['venue']['name'],
                     'id': event['venue']['id'],
                     'region': event['venue']['location']['street'],
                     'country': event['venue']['location']['country'],
                     'artists': my_arts,
                     'artist_image': event['image'][-1]['#text'],
                     'venue_image': event['venue']['image'][-1]['#text'],
                     'headliner': event['artists']['headliner']  }
            events.append(event)
    except:
        log("Error when handling LastFM results")
    return events
    
    
def HandleLastFMAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    try:
        for album in results['topalbums']['album']:
            album = {'artist': album['artist']['name'],
                     'mbid': album['mbid'],
                     'name':album['name']  }
            albums.append(album)
    except:
        log("Error when handling LastFM results")
    return albums
    
    
def HandleLastFMShoutResult(results):
    shouts = []
    log("starting HandleLastFMShoutResult")
    try:
        for shout in results['shouts']['shout']:
            newshout = {'comment': shout['body'],
                        'author': shout['author'],
                        'date':shout['date']  }
            shouts.append(newshout)
    except:
        log("Error when handling LastFM Shout results")
    return shouts
    
def HandleTheMovieDBMovieResult(results):
    movies = []
    log("starting HandleLastFMShoutResult")
    try:
        for movie in results['results']:
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
    
    
def HandleLastFMTracksResult(results):
    artists = []
    log("starting HandleLastFMTracksResult")
    try:
        for artist in results['artists']['artist']:
            artist = {'Title': artist['name'],
                      'Thumb': artist['image'][-1]['#text'],
                      'Listeners':artist['listeners']  }
            artists.append(artist)
    except:
        log("Error when handling LastFM TopArtists results")
    return artists
    
    
''' old BandsInTown Way
def GetEvents(id,getall = False): # converted to api 2.0
    if getall:
        url = 'http://api.bandsintown.com/artists/mbid_%s/events?format=json&app_id=%s&date=all' % (id, bandsintown_apikey)
    else:
        url = 'http://api.bandsintown.com/artists/mbid_%s/events.json?api_version=2.0&app_id=%s' % (id, bandsintown_apikey)
    log(url)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        if not results:
            GetEvents(id,True)
    except:
        log("Error when finding artist-related events from" + url)
    return HandleBandsInTownResult(results)
   ''' 
    
def GetEvents(id,pastevents = False):
    if pastevents:
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getpastevents&mbid=%s&api_key=%s&format=json' % (id, lastfm_apikey)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&mbid=%s&api_key=%s&format=json' % (id, lastfm_apikey)
    filename = Addon_Data_Path + "/concerts" + id + str(pastevents) +".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
    else:
        try:
            response = GetStringFromUrl(url)
            save_to_file(response,"artistconcerts" + id + str(pastevents),Addon_Data_Path)
            results = json.loads(response)
            return HandleLastFMEventResult(results)
        except:
            log("Error when finding artist-related events from" + url)
            return []
    
    
def GetTopArtists():
    url = 'http://ws.audioscrobbler.com/2.0/?method=chart.getTopArtists&api_key=%s&format=json' % (lastfm_apikey)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        return HandleLastFMTracksResult(results)
    except:
        log("Error when finding artist top-tracks from" + url)
        return []
    
def GetShouts(artistname,albumtitle):
    url = 'http://ws.audioscrobbler.com/2.0/?method=album.getshouts&artist=%s&album=%s&api_key=%s&format=json' % (urllib.quote_plus(artistname),urllib.quote_plus(albumtitle), lastfm_apikey)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        return HandleLastFMShoutResult(results)
    except:
        log("Error when finding shouts from" + url)
        return []
    
def GetTopAlbums(username):
    url = 'http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=%s&api_key=%s&format=json' % (urllib.quote_plus(username), lastfm_apikey)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        return HandleLastFMAlbumResult(results)
    except:
        log("Error when finding topalbums from" + url)
        return []

    
def GetSimilarById(m_id):
    similars = []
    filename = Addon_Data_Path + "/similar" + m_id +".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 2409600:
        similars = read_from_file(filename)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&mbid=%s&api_key=%s' % (m_id, lastfm_apikey)
        try:
            ret = GetStringFromUrl(url)
            curXML = xml.dom.minidom.parseString(ret)
            curXMLs = curXML.getElementsByTagName('lfm')
        except:
            log("error when getting info from LastFM")
            return None
        if len(curXMLs) > 0:
            curXML = curXMLs[0]
        else:
            log('No <lfm> found - printing retrieved xml:')
            print ret
            return None    
        curXMLs = curXML.getElementsByTagName('similarartists')
        if len(curXMLs) > 0:
            curXML = curXMLs[0]
        else:
            log('No <similarartists> found - printing retrieved xml:')
            print ret
            return None        
        artistXMLs = curXML.getElementsByTagName('artist')
        for artistXML in artistXMLs:
            artist = {"name": GetValue(artistXML, 'name'),
                      "mbid": GetValue(artistXML, 'mbid')}
            similars.append(artist)
        log('Found %i Similar artists in last.FM' % len(similars))
    return similars
    
    
def GetNearEvents(tag = False,festivalsonly = False):
    import time
    results = []
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    country = 'Poland' #settings.getSetting('country')
    city = 'Wroclaw' #settings.getSetting('city')
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    filename = Addon_Data_Path + "/concerts" + festivalsonly + str(tag) +".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        log("loaded from file:")
        log(results)
    else:
        if not tag:
            url = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&api_key=%s&format=json&limit=50&festivalsonly=%s' % (lastfm_apikey,festivalsonly)
        else:
            url = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&api_key=%s&format=json&limit=50&tag=%s&festivalsonly=%s' % (lastfm_apikey,urllib.quote_plus(tag),festivalsonly)   
        try:
            response = GetStringFromUrl(url)
            save_to_file(response,"concerts" + festivalsonly + str(tag),Addon_Data_Path)
            results = json.loads(response)
            log("refreshed NearEvents Info:")
            log(results)
        except:
            log("error getting concert data from " + url)
            return []
    return HandleLastFMEventResult(results)

            
def GetVenueEvents(id = ""):
    import time
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    filename = Addon_Data_Path + "/concerts" + id + ".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=venue.getevents&api_key=%s&venue=%s&format=json' % (lastfm_apikey,id)
        log('request: %s' % url)
        try:
            response = GetStringFromUrl(url)
            save_to_file(response,"concerts" + id, Addon_Data_Path)
            results = json.loads(response)
            return HandleLastFMEventResult(results)
        except:
            results = []
            log("error getting concert data from " + url)
            return []
    

def GetArtistNearEvents(Artists): # not possible with api 2.0
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    ArtistStr = ''
    for art in Artists:
        if len(ArtistStr) > 0:
             ArtistStr = ArtistStr + '&'
        ArtistStr = ArtistStr + 'artists[]=' + urllib.quote(art['name'])     
    url = 'http://api.bandsintown.com/events/search?%sformat=json&location=use_geoip&api_version=2.0&app_id=%s' % (ArtistStr, bandsintown_apikey)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        return HandleBandsInTownResult(results)
    except:
        log("error when getting artist data from " + url)
        return []
