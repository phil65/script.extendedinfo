import xbmcaddon, os, xbmc, xbmcvfs, time
import simplejson as json
from Utils import *
import urllib

AudioDB_apikey = '58353d43204d68753987fl'
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )
__addon__        = xbmcaddon.Addon()

def GetAudioDBData(url = "", cache_days = 0):
    from base64 import b64encode
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    log("trying to load "  + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        try:
            url = 'http://www.theaudiodb.com/api/v1/json/%s/%s' % (AudioDB_apikey, url)
            response = GetStringFromUrl(url)
            results = json.loads(response)
            save_to_file(results,filename,Addon_Data_Path)
            return results
        except:
            log("GetAudioDBData failed with answer: " + response)
            return []
        
def HandleAudioDBAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    if 'album' in results and results['album']:
        for album in results['album']:
            localdescription = 'strDescription' + __addon__.getSetting("LanguageID").upper()
            if localdescription in album and album[localdescription] <> None:
                Description = album.get(localdescription,"")
            elif 'strDescriptionEN' in album:
                Description = album['strDescriptionEN']
            elif 'strDescription' in album:
                Description = album['strDescription']
            else:
                Description = ""
            if album.get('strReview') <> None and album['strReview']:
                Description += "[CR][CR][B]REVIEW:[/B][CR][CR]" + album["strReview"]
            album = {'artist': album['strArtist'],
                     'Label2': album['strArtist'],
                     'mbid': album['strMusicBrainzID'],
                     'id': album['idAlbum'],
                     'audiodbid': album['idAlbum'],
                     'Description': Description,
                     'Path': "",
                     'Plot': Description,
                     'Genre': album['strSubGenre'],
                     'Mood': album['strMood'],
                     'Style': album['strSpeed'],
                     'Theme': album['strTheme'],
                     'Type': album['strReleaseFormat'],
                     'thumb': album['strAlbumThumb'],
                     'Icon': album['strAlbumThumb'],
                     'year': album['intYearReleased'],
                     'Sales': album['intSales'],
                     'name':album['strAlbum'],
                     'Label':album['strAlbum']  }
            albums.append(album)
        albums = CompareAlbumWithLibrary(albums)
    else:
        log("Error when handling HandleAudioDBAlbumResult results")
    return albums
    
def HandleAudioDBTrackResult(results):
    tracks = []
    log("starting HandleAudioDBTrackResult")
 #   prettyprint(results)
    if 'track' in results and results['track']:
        for track in results['track']:
            if 'strMusicVid' in track and track['strMusicVid'] <> None:
                Thumb = "http://i.ytimg.com/vi/" + ExtractYoutubeID(track.get('strMusicVid','')) + "/0.jpg"
                Path = ConvertYoutubeURL(track['strMusicVid'])
            else:
                Thumb = ""
                Path = ""
            track = {'Track': track['strTrack'],
                     'Artist': track['strArtist'],
                     'mbid': track['strMusicBrainzID'],
                     'Album': track['strAlbum'],
                     'Thumb': Thumb,
                     'Path': Path ,
                     'Label':track['strTrack']  }
            tracks.append(track)
    else:
        log("Error when handling HandleAudioDBTrackResult results")
        prettyprint(results)
    return tracks
    
def HandleAudioDBMusicVideoResult(results):
    mvids = []
    log("starting HandleAudioDBMusicVideoResult")
 #   prettyprint(results)
    if 'mvids' in results and results['mvids']:
        for mvid in results['mvids']:
            mvid = {'Track': mvid['strTrack'],
                     'Description': mvid['strDescriptionEN'],
                     'id': mvid['idTrack'],
                     'Thumb': "http://i.ytimg.com/vi/" + ExtractYoutubeID(mvid.get('strMusicVid','')) + "/0.jpg",
                     'Path': ConvertYoutubeURL(mvid['strMusicVid']),
                     'Label':mvid['strTrack']  }
            mvids.append(mvid)
    else:
        log("Error when handling HandleAudioDBMusicVideoResult results")
    return mvids
       
def GetExtendedAudioDBInfo(results):
    artists = []
    log("starting GetExtendedAudioDBInfo")
    if 'artists' in results and results['artists']:
        for artist in results['artists']:
            localbio = 'strBiography' + __addon__.getSetting("LanguageID").upper()
            if localbio in artist and artist[localbio] <> None:
                Description = artist.get(localbio,"")
            elif 'strBiographyEN' in artist and artist['strBiographyEN'] <> None:
                Description = artist.get('strBiographyEN',"")
            elif 'strBiography' in artist:
                Description = artist.get('strBiography',"")
            else:
                Description = ""
            if "strReview" in artist:
                Description += "[CR]" + artist.get('strReview',"")
            artist = {'artist': artist.get('strArtist',""),
                     'mbid': artist.get('strMusicBrainzID',""),
                     'Banner': artist.get('strArtistBanner',""),
                     'Logo': artist.get('strArtistLogo',""),
                     'Fanart': artist.get('strArtistFanart',""),
                     'Fanart2': artist.get('strArtistFanart2',""),
                     'Fanart3': artist.get('strArtistFanart3',""),
                     'Born': artist.get('intBornYear',""),
                     'Formed': artist.get('intFormedYear',""),
                     'Died': artist.get('intDiedYear',""),
                     'Country': artist.get('strCountryCode',""),
                     'Website': artist.get('strWebsite',""),
                     'Twitter': artist.get('strTwitter',""),
                     'Facebook': artist.get('strFacebook',""),
                     'Gender': artist.get('strGender',""),
                     'Banner': artist.get('strArtistBanner',""),
                     'audiodbid': artist.get('idArtist',""),
                     'Description': Description,
                     'Plot': Description,
                     'Path': "",
                     'Genre': artist.get('strSubGenre',""),
                     'Label2': artist.get('strSubGenre',""),
                     'Thumb': artist.get('strArtistThumb',""),
                     'Art(Thumb)': artist.get('strArtistThumb',""),
                     'Members':artist.get('intMembers',"")  }
            artists.append(artist)
    else:
        log("Error when handling GetExtendedAudioDBInfo results")
    if len(artists) > 0:
        return artists[0]
    else:
        return {}
       
def GetDiscography(search_string):
    url = 'searchalbum.php?s=%s' % (urllib.quote_plus(search_string))
    results = GetAudioDBData(url)
    if True:
        return HandleAudioDBAlbumResult(results)
    else:
        return []
        
def GetArtistDetails(search_string):
    url = 'search.php?s=%s' % (urllib.quote_plus(search_string))
    results = GetAudioDBData(url)
   # prettyprint(results)
    if True:
        return GetExtendedAudioDBInfo(results)
    else:
        return []
              
def GetMostLovedTracks(search_string = "", mbid = ""):
    if mbid:
        pass
    else:
        url = 'track-top10.php?s=%s' % (urllib.quote_plus(search_string))
    log("GetMostLoveTracks URL:" + url)
    results = GetAudioDBData(url)
    if True:
        return HandleAudioDBTrackResult(results)
    else:
        return []
        
        
def GetAlbumDetails(audiodbid = "", mbid = ""):
    if audiodbid:
        url = 'album.php?m=%s' % (audiodbid)
    elif mbid:
        url = 'album-mb.php?i=%s' % (mbid)
    results = GetAudioDBData(url)
  #  prettyprint(results)
    if True:
        return HandleAudioDBAlbumResult(results)[0]
    else:
        return []
        
def GetMusicVideos(audiodbid):
    url = 'mvid.php?i=%s' % (audiodbid)
    results = GetAudioDBData(url)
    if True:
        return HandleAudioDBMusicVideoResult(results)
    else:
        return []
        
def GetTrackDetails(audiodbid):
    url = 'track.php?m=%s' % (audiodbid)
    results = GetAudioDBData(url)
    if True:
        return HandleAudioDBTrackResult(results)
    else:
        return []
        
