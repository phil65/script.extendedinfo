import xbmcaddon
import os
import xbmc
import xbmcvfs
import time
import sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
from Utils import *
import urllib

lastfm_apikey = '6c14e451cd2d480d503374ff8c8f4e2b'
googlemaps_key_old = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))


def HandleLastFMEventResult(results):
    events = []
    if "events" in results:
        if "@attr" in results["events"]:
            if int(results["events"]["@attr"]["total"]) == 1:
                results['events']['event'] = [results['events']['event']]
            for event in results['events']['event']:
                artists = event['artists']['artist']
                if isinstance(artists, list):
                    my_arts = ' / '.join(artists)
                else:
                    my_arts = artists
                lat = ""
                lon = ""

                try:
                    if event['venue']['location']['geo:point']['geo:long']:
                        lon = event['venue']['location']['geo:point']['geo:long']
                        lat = event['venue']['location']['geo:point']['geo:lat']
                        search_string = lat + "," + lon
                    elif event['venue']['location']['street']:
                        search_string = urllib.quote_plus(event['venue']['location']['city'] + " " + event['venue']['location']['street'])
                    elif event['venue']['location']['city']:
                        search_string = urllib.quote_plus(event['venue']['location']['city'] + " " + event['venue']['name'])
                    else:
                        search_string = urllib.quote_plus(event['venue']['name'])
                except:
                    search_string = ""
                googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_old)
                event = {'date': event['startDate'][:-3],
                         'name': event['venue']['name'],
                         'id': event['venue']['id'],
                         'street': event['venue']['location']['street'],
                         'eventname': event['title'],
                         'website': event['website'],
                         'description': cleanText(event['description']),
                         'postalcode': event['venue']['location']['postalcode'],
                         'city': event['venue']['location']['city'],
                         'country': event['venue']['location']['country'],
                         'geolong': event['venue']['location']['geo:point']['geo:long'],
                         'geolat': event['venue']['location']['geo:point']['geo:lat'],
                         'artists': my_arts,
                         'googlemap': googlemap,
                         'artist_image': event['image'][-1]['#text'],
                         'venue_image': event['venue']['image'][-1]['#text'],
                         'headliner': event['artists']['headliner']}
                events.append(event)
    elif "error" in results:
        Notify("Error", results["message"])
    else:
        log("Error in HandleLastFMEventResult. JSON query follows:")
     #   prettyprint(results)
    return events


def HandleLastFMAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    if 'topalbums' in results:
        for album in results['topalbums']['album']:
            album = {'artist': album['artist']['name'],
                     'mbid': album['mbid'],
                     'thumb': album['image'][-1]['#text'],
                     'name': album['name']}
            albums.append(album)
    else:
        log("No Info in JSON answer:")
        prettyprint(results)
    return albums


def HandleLastFMShoutResult(results):
    shouts = []
    log("starting HandleLastFMShoutResult")
    try:
        for shout in results['shouts']['shout']:
            newshout = {'comment': shout['body'],
                        'author': shout['author'],
                        'date': shout['date'][4:]}
            shouts.append(newshout)
    except Exception as e:
        log("Error when handling LastFM Shout results")
        log(e)
        prettyprint(results)
    return shouts


def HandleLastFMTrackResult(results):
    log("starting HandleLastFMTrackResult")
    try:
       # prettyprint(results)
        if "wiki" in results['track']:
            summary = cleanText(results['track']['wiki']['summary'])
        else:
            summary = ""
        TrackInfo = {'playcount': str(results['track']['playcount']),
                     'Thumb': str(results['track']['playcount']),
                     'summary': summary}
    except Exception as e:
        log("Error when handling LastFM Track results")
        log(e)
        prettyprint(results)
    return TrackInfo


def HandleLastFMArtistResult(results):
    artists = []
    log("starting HandleLastFMArtistResult")
    try:
        for artist in results['artist']:
            if 'name' in artist:
                listeners = int(artist.get('listeners', 0))
                artist = {'Title': artist['name'],
                          'name': artist['name'],
                          'mbid': artist['mbid'],
                          'Thumb': artist['image'][-1]['#text'],
                          'Listeners': format(listeners, ",d")}
                artists.append(artist)
    except Exception as e:
        log("Error when handling LastFM TopArtists results")
        log(e)
        prettyprint(results)
    return artists


def GetEvents(id, pastevents=False):
    if pastevents:
        url = 'method=artist.getpastevents&mbid=%s' % (id)
    else:
        url = 'method=artist.getevents&mbid=%s' % (id)
    results = GetLastFMData(url, 1)
    try:
        return HandleLastFMEventResult(results)
    except:
        log("Error in GetEvents()")
        return []


def GetLastFMData(url="", cache_days=14):
    from base64 import b64encode
    filename = b64encode(url).replace("/", "XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    log("trying to load " + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&%s' % (lastfm_apikey, url)
        response = GetStringFromUrl(url)
        try:
            results = simplejson.loads(response)
            save_to_file(results, filename, Addon_Data_Path)
            return results
        except Exception as e:
            log("Error in GetLastFMData. No Internet connection?")
            log(e)
            return []


def GetTopArtists():
    results = GetLastFMData("method=chart.getTopArtists&limit=100")
    if "artists" in results:
        return HandleLastFMArtistResult(results['artists'])
    else:
        log("Error when finding artist top-tracks.")
        return []


def GetAlbumShouts(artistname, albumtitle):
    url = 'method=album.GetAlbumShouts&artist=%s&album=%s' % (urllib.quote_plus(artistname), urllib.quote_plus(albumtitle))
    results = GetLastFMData(url)
    try:
        return HandleLastFMShoutResult(results)
    except Exception as e:
        log(e)
        log("Error when finding shouts from" + url)
        return []


def GetArtistShouts(artistname):
    url = 'method=artist.GetShouts&artist=%s' % (urllib.quote_plus(artistname))
    results = GetLastFMData(url)
    try:
        return HandleLastFMShoutResult(results)
    except Exception as e:
        log(e)
        log("Error when finding shouts from" + url)
        return []


def GetTrackShouts(artistname, tracktitle):
    url = 'method=album.GetAlbumShouts&artist=%s&track=%s' % (urllib.quote_plus(artistname), urllib.quote_plus(tracktitle))
    results = GetLastFMData(url)
    try:
        return HandleLastFMShoutResult(results)
    except Exception as e:
        log(e)
        log("Error when finding shouts from" + url)
        return []


def GetEventShouts(eventid):
    url = 'method=event.GetShouts&event=%s' % (eventid)
    results = GetLastFMData(url)
    try:
        return HandleLastFMShoutResult(results)
    except Exception as e:
        log(e)
        log("Error when finding shouts from" + url)
        return []


def GetArtistTopAlbums(mbid):
    url = 'method=artist.gettopalbums&mbid=%s' % (mbid)
    results = GetLastFMData(url)
    try:
        return HandleLastFMAlbumResult(results)
    except Exception as e:
        log(e)
        log("Error when finding topalbums from" + url)
        return []


def GetSimilarById(m_id):
    url = 'method=artist.getsimilar&mbid=%s&limit=400' % (m_id)
    results = GetLastFMData(url)
    try:
        return HandleLastFMArtistResult(results['similarartists'])
    except Exception as e:
        log(e)
        log("Error when finding SimilarById from" + url)
        return []


def GetNearEvents(tag=False, festivalsonly=False, lat="", lon=""):
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    url = 'method=geo.getevents&festivalsonly=%s&limit=40' % (festivalsonly)
    if tag:
        url = url + '&tag=%s' % (urllib.quote_plus(tag))
    if lat:
        url = url + '&lat=%s&long=%s' % (lat, lon)  # &distance=60
    results = GetLastFMData(url, 1)
 #   prettyprint(results)
    return HandleLastFMEventResult(results)


def GetVenueEvents(id=""):
    url = 'method=venue.getevents&venue=%s' % (id)
    results = GetLastFMData(url, 1)
    try:
        return HandleLastFMEventResult(results)
    except:
        log("GetVenueEvents: error getting concert data from " + url)
        return []


def GetTrackInfo(artist="", track=""):
    url = 'method=track.getInfo&artist=%s&track=%s' % (urllib.quote_plus(artist), urllib.quote_plus(track))
    results = GetLastFMData(url)
    if True:
        return HandleLastFMTrackResult(results)
    else:
        log("GetVenueEvents: error getting TrackInfo data from " + url)
        return []

