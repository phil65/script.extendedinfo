import xbmcaddon
import simplejson as json
from Utils import log, GetStringFromUrl, GetValue
import xml.dom.minidom
import urllib

bandsintown_apikey = 'xbmc_open_source_media_center'
lastfm_apikey = 'bb258101395ce46c63843bd6261e3fc8'

def HandleResult(results):
    events = []
    for event in results:
        try:
            date = event['datetime']
            date = date.replace("T", " - ").replace(":00", "",1)
            venue = event['venue']
            city = venue['city']
            name = venue['name']
            region = venue['region']
            country = venue['country']
            artists = event['artists']
            my_arts = ''
            for art in artists:
                my_arts += ' / '
                my_arts += art['name']
            my_arts = my_arts.replace(" / ", "",1)        
            event = {'date': date, 'city': city, 'name':name, 'region':region, 'country':country, 'artists':my_arts  }
            events.append(event)
        except: pass
    return events
    
def HandleLastFMResult(results):
    events = []
    log("starting xyz")
    for event in results['events']['event']:
        log(event)
        date = event['startDate']
        venue = event['venue']['name']
        city = event['venue']['location']['city']
        name = event['venue']['name']
        region = event['venue']['location']['street']
        country = event['venue']['location']['country']
        artists = event['artists']['artist']
        my_arts = ''
        if isinstance(artists, list):
            my_arts = ' / '.join(artists)
        else:
            my_arts = artists
        event = {'date': date, 'city': city, 'name':name, 'region':region, 'country':country, 'artists':my_arts  }
        log(event)
        events.append(event)
    return events

def GetEvents(id): # converted to api 2.0
    url = 'http://api.bandsintown.com/artists/mbid_%s/events.json?api_version=2.0&app_id=%s' % (id, bandsintown_apikey)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
    except:
        log("Error when finding artist-related events from" + url)
    return HandleResult(results)

    
def GetSimilarById(m_id):
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
    similars = []
    for artistXML in artistXMLs:
        artist = {"name": GetValue(artistXML, 'name'), "mbid": GetValue(artistXML, 'mbid')}
        similars.append(artist)
    log('Found %i Similar artists in last.FM' % len(similars))
    return similars
    
    
def GetNearEvents(): # not possible with api 2.0
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    country = 'Poland' #settings.getSetting('country')
    city = 'Wroclaw' #settings.getSetting('city')
    url = 'http://ws.audioscrobbler.com/2.0/?method=geo.getevents&api_key=%s&format=json&limit=50' % lastfm_apikey
    log('request: %s' % url)
    try:
        response = GetStringFromUrl(url)
        log(response)
      #  response = unicode(response, 'utf-8', errors='ignore')
        results = json.loads(response)
        log(results)
    except:
        results = []
        log("error getting concert data from " + url)
    return HandleLastFMResult(results)

def GetArtistNearEvents(Artists): # not possible with api 2.0
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    ArtistStr = ''
    for art in Artists:
        if len(ArtistStr) > 0:
             ArtistStr = ArtistStr + '&'
        ArtistStr = ArtistStr + 'artists[]=' + urllib.quote(art['name'])     
    url = 'http://api.bandsintown.com/events/search?%sformat=json&location=use_geoip&api_version=2.0&app_id=%s' % (ArtistStr, bandsintown_apikey)
    log('request: %s' % url)
    try:
        response = GetStringFromUrl(url)
        results = json.loads(response)
    except:
        log("error when getting artist data from " + url)
    return HandleResult(results)
