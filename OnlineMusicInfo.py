import xbmcaddon, os, xbmc, xbmcvfs, time
import simplejson as json
from Utils import *
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
    log("starting HandleLastFMEventResult")
    if True:
        for event in results['events']['event']:
            artists = event['artists']['artist']
            if isinstance(artists, list):
                my_arts = ' / '.join(artists)
            else:
                my_arts = artists
            lat = ""
            lon = ""               
            if event['venue']['location']['geo:point']['geo:long']:
                lon = event['venue']['location']['geo:point']['geo:long']
                lat = event['venue']['location']['geo:point']['geo:lat']
                search_string = ""
            elif event['venue']['location']['street']:
                search_string = event['venue']['location']['city'] + " " + event['venue']['location']['street']
            elif event['venue']['location']['city']:
                search_string = event['venue']['location']['city'] + " " + event['venue']['name']               
            else:
                search_string = event['venue']['name']
            log("search string vor venue: " + search_string)
            from MiscScraper import GetGoogleMap
            googlemap = GetGoogleMap(mode = "normal",search_string = search_string,zoomlevel = "13",type = "roadmap",aspect = "square", lat=lat,lon=lon,direction = "")
            event = {'date': event['startDate'],
                     'name': event['venue']['name'],
                     'id': event['venue']['id'],
                     'street': event['venue']['location']['street'],
                     'eventname': event['title'],
                     'website': event['website'],
                     'description': cleanText(event['description']),
                    # 'description': event['description'], ticket missing
                     'city': event['venue']['location']['postalcode'] + " " + event['venue']['location']['city'],
                     'country': event['venue']['location']['country'],
                     'geolong': event['venue']['location']['geo:point']['geo:long'],
                     'geolat': event['venue']['location']['geo:point']['geo:lat'],
                     'artists': my_arts,
                     'googlemap': googlemap,
                     'artist_image': event['image'][-1]['#text'],
                     'venue_image': event['venue']['image'][-1]['#text'],
                     'headliner': event['artists']['headliner']  }
            events.append(event)
    else:
        log("Error when handling LastFM results")
    return events
       
def HandleLastFMAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    if True:
        for album in results['topalbums']['album']:
            album = {'artist': album['artist']['name'],
                     'mbid': album['mbid'],
                     'thumb': album['image'][-1]['#text'],
                     'name':album['name']  }
            albums.append(album)
    else:
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
           
def HandleLastFMTracksResult(results):
    artists = []
    log("starting HandleLastFMTracksResult")
    if True:
        for artist in results['artist']:
            artist = {'Title': artist['name'],
                      'name': artist['name'],
                      'mbid': artist['mbid'],
                      'Thumb': artist['image'][-1]['#text'],
                      'Listeners':artist.get('listeners',"")  }
            artists.append(artist)
    else:
        log("Error when handling LastFM TopArtists results")
    return artists
    
def GetEvents(id,pastevents = False):
    if pastevents:
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getpastevents&mbid=%s&api_key=%s&format=json' % (id, lastfm_apikey)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&mbid=%s&api_key=%s&format=json' % (id, lastfm_apikey)
    filename = Addon_Data_Path + "/concerts" + str(id) + str(pastevents) +".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        return HandleLastFMEventResult(results)
    else:
        try:
            response = GetStringFromUrl(url)
            results = json.loads(response)
            save_to_file(results,"artistconcerts" + id + str(pastevents),Addon_Data_Path)
            return HandleLastFMEventResult(results)
        except:
            log("Error when finding artist-related events from" + url)
            return []

def GetLastFMData(url = "", cache_days = 14):
    from base64 import b64encode
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    log("trying to load "  + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&%s' % (lastfm_apikey, url)
        response = GetStringFromUrl(url)
        results = json.loads(response)
        save_to_file(results,filename,Addon_Data_Path)
        return results
                      
def GetTopArtists():
    results = GetLastFMData("method=chart.getTopArtists&limit=100")
    if True:
        return HandleLastFMTracksResult(results['artists'])
    else:
        log("Error when finding artist top-tracks from" + url)
        return []
    
def GetShouts(artistname,albumtitle):
    url = 'method=album.getshouts&artist=%s&album=%s' % (urllib.quote_plus(artistname),urllib.quote_plus(albumtitle))
    results = GetLastFMData(url)
    if True:
        return HandleLastFMShoutResult(results)
    else:
        log("Error when finding shouts from" + url)
        return []
    
def GetArtistTopAlbums(mbid):
    url = 'method=artist.gettopalbums&mbid=%s' % (mbid)
    results = GetLastFMData(url)
    if True:
        return HandleLastFMAlbumResult(results)
    else:
        log("Error when finding topalbums from" + url)
        return []
        
def GetSimilarById(m_id):
    url = 'method=artist.getsimilar&mbid=%s' % (m_id)
    results = GetLastFMData(url)
    if True:
        return HandleLastFMTracksResult(results['similarartists'])
    else:
        log("Error when finding SimilarById from" + url)
        return []
        
def GetNearEvents(tag = False,festivalsonly = False,lat = "", lon = ""):
    import time
    results = []
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    filename = Addon_Data_Path + "/NearEvents" + festivalsonly + str(tag) + str(lat) + str(lon) +".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        log("Results loaded from file: " + filename)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&api_key=%s&format=json&limit=50&festivalsonly=%s' % (lastfm_apikey,festivalsonly)
        if tag:
            url = url + '&tag=%s' % (urllib.quote_plus(tag))  
        if lat:
            url = url + '&lat=%s&long=%s&distance=60' % (lat,lon)  
        if True:
            response = GetStringFromUrl(url)
            results = json.loads(response)
            save_to_file(results,"NearEvents" + festivalsonly + str(tag) + str(lat) + str(lon),Addon_Data_Path)
        else:
            log("error getting concert data from " + url)
            return []
    return HandleLastFMEventResult(results)
           
def GetVenueEvents(id = ""):
    url = 'method=venue.getevents&venue=%s' % (id)
    log('GetVenueEvents request: %s' % url)
    results = GetLastFMData(url)
    if True:
        return HandleLastFMEventResult(results)
    else:
        log("GetVenueEvents: error getting concert data from " + url)
        return []

def GetArtistNearEvents(Artists): # not possible with api 2.0
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    ArtistStr = ''
    for art in Artists:
        if len(ArtistStr) > 0:
             ArtistStr = ArtistStr + '&'
        ArtistStr = ArtistStr + 'artists[]=' + urllib.quote(art['name'])     
    url = 'http://api.bandsintown.com/events/search?%sformat=json&location=use_geoip&api_version=2.0&app_id=%s' % (ArtistStr, bandsintown_apikey)
    if True:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        return HandleBandsInTownResult(results)
    else:
        log("GetArtistNearEvents: error when getting artist data from " + url)
        return []
