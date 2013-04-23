import xbmcaddon, os, xbmc, xbmcvfs, time
import simplejson as json
from Utils import *
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
            else:
                search_string = event['venue']['name']
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
            log(['image'])
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
        for artist in results['artists']['artist']:
            artist = {'Title': artist['name'],
                      'mbid': artist['mbid'],
                      'Thumb': artist['image'][-1]['#text'],
                      'Listeners':artist['listeners']  }
            artists.append(artist)
    else:
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
    
    
def GetTopArtists():
    url = 'http://ws.audioscrobbler.com/2.0/?method=chart.getTopArtists&api_key=%s&limit=100&format=json' % (lastfm_apikey)
    filename = Addon_Data_Path + "/GetTopArtists.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        return HandleLastFMTracksResult(results)
    else:
        if True:
            response = GetStringFromUrl(url)
            results = json.loads(response)
            save_to_file(results,"GetTopArtists",Addon_Data_Path)
            return HandleLastFMTracksResult(results)
        else:
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
    
def GetArtistTopAlbums(mbid):
    url = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&mbid=%s&api_key=%s&format=json' % (mbid, lastfm_apikey)
    log(url)
    if True:
        response = GetStringFromUrl(url)
        results = json.loads(response)
        return HandleLastFMAlbumResult(results)
    else:
        log("Error when finding topalbums from" + url)
        return []
        
def GetSimilarById(m_id):
    similars = []
    filename = Addon_Data_Path + "/GetSimilarById" + m_id +".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 2409600:
        similars = read_from_file(filename)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&mbid=%s&api_key=%s' % (m_id, lastfm_apikey)
        if True:
            ret = GetStringFromUrl(url)
            curXML = xml.dom.minidom.parseString(ret)
            curXMLs = curXML.getElementsByTagName('lfm')
        else:
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
        
def GetNearEvents(tag = False,festivalsonly = False,lat = "", lon = ""):
    import time
    results = []
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    country = 'Poland' #settings.getSetting('country')
    city = 'Wroclaw' #settings.getSetting('city')
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
    import time
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    filename = Addon_Data_Path + "/VenueEvents" + id + ".txt"
  #  if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        return HandleLastFMEventResult(results)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?method=venue.getevents&api_key=%s&venue=%s&format=json' % (lastfm_apikey,id)
        log('GetVenueEvents request: %s' % url)
        if True:
            response = GetStringFromUrl(url)
            results = json.loads(response)
            save_to_file(results,"VenueEvents" + id, Addon_Data_Path)
            return HandleLastFMEventResult(results)
        else:
            results = []
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
