import xbmcaddon, os, xbmc, xbmcvfs, time
import simplejson as json
from Utils import *
import urllib

AudioDB_apikey = '58353d43204d68753987fl'
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def GetAudioDBData(url = "", cache_days = 0):
    from base64 import b64encode
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    log("trying to load "  + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = 'http://www.theaudiodb.com/api/v1/json/%s/%s' % (AudioDB_apikey, url)
        response = GetStringFromUrl(url)
        results = json.loads(response)
        log("look here")
        save_to_file(results,filename,Addon_Data_Path)
        return results
        
def HandleAudioDBAlbumResult(results):
    albums = []
    log("starting HandleLastFMAlbumResult")
    prettyprint(results)
    if 'album' in results and results['album']:
        for album in results['album']:
            if 'strDescriptionEN' in album:
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
            if 'strTrackThumb' in track:
                Thumb = track['strTrackThumb']
            elif 'strMusicVidScreen1' in track:
                Thumb = track['strMusicVidScreen1']
            else:
                Thumb = ""
            track = {'Track': track['strTrack'],
                     'Artist': track['strArtist'],
                     'mbid': track['strMusicBrainzID'],
                     'Album': track['strAlbum'],
                     'Thumb':Thumb,
                     'Path': track['strMusicVid'],
                     'Label':track['strTrack']  }
            tracks.append(track)
    else:
        log("Error when handling HandleAudioDBTrackResult results")
    return tracks
    
    
    
def GetExtendedAudioDBInfo(results):
    artists = []
    log("starting GetExtendedAudioDBInfo")
    prettyprint(results)
    if 'artists' in results and results['artists']:
        for artist in results['artists']:
            if 'strBiographyEN' in artist:
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
    log(url)
    results = GetAudioDBData(url)
    prettyprint(results)
    if True:
        return HandleAudioDBTrackResult(results)
    else:
        return []
        
        
def GetAlbumDetails(audiodbid):
    url = 'album.php?m=%s' % (audiodbid)
    results = GetAudioDBData(url)
  #  prettyprint(results)
    if True:
        return HandleAudioDBAlbumResult(results)[0]
    else:
        return []
        
