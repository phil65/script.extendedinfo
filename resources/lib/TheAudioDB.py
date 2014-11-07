import xbmcaddon
import os
import xbmc
import simplejson as json
from Utils import *
import urllib

AudioDB_apikey = '58353d43204d68753987fl'
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))
__addon__ = xbmcaddon.Addon()
base_url = 'http://www.theaudiodb.com/api/v1/json/%s/' % (AudioDB_apikey)


def HandleAudioDBAlbumResult(results):
    albums = []
    if 'album' in results and results['album']:
        for album in results['album']:
            localdescription = 'strDescription' + __addon__.getSetting("LanguageID").upper()
            if localdescription in album and album[localdescription] is not None:
                Description = album.get(localdescription, "")
            elif 'strDescriptionEN' in album:
                Description = album['strDescriptionEN']
            elif 'strDescription' in album:
                Description = album['strDescription']
            else:
                Description = ""
            review = album.get('strReview')
            if review and str(review) != "null":
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
                     'name': album['strAlbum'],
                     'Label': album['strAlbum']}
            albums.append(album)
        albums = CompareAlbumWithLibrary(albums)
    else:
        log("Error when handling HandleAudioDBAlbumResult results")
    return albums


def HandleAudioDBTrackResult(results):
    tracks = []
 #   prettyprint(results)
    if 'track' in results and results['track']:
        for track in results['track']:
            if 'strMusicVid' in track and track['strMusicVid'] is not None:
                Thumb = "http://i.ytimg.com/vi/" + ExtractYoutubeID(track.get('strMusicVid', '')) + "/0.jpg"
                Path = ConvertYoutubeURL(track['strMusicVid'])
            else:
                Thumb = ""
                Path = ""
            track = {'Track': track['strTrack'],
                     'Artist': track['strArtist'],
                     'mbid': track['strMusicBrainzID'],
                     'Album': track['strAlbum'],
                     'Thumb': Thumb,
                     'Path': Path,
                     'Label': track['strTrack']}
            tracks.append(track)
    else:
        log("Error when handling HandleAudioDBTrackResult results")
        prettyprint(results)
    return tracks


def HandleAudioDBMusicVideoResult(results):
    mvids = []
 #   prettyprint(results)
    if 'mvids' in results and results['mvids']:
        for mvid in results['mvids']:
            mvid = {'Track': mvid['strTrack'],
                    'Description': mvid['strDescriptionEN'],
                    'id': mvid['idTrack'],
                    'Thumb': "http://i.ytimg.com/vi/" + ExtractYoutubeID(mvid.get('strMusicVid', '')) + "/0.jpg",
                    'Path': 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % ConvertYoutubeURL(mvid['strMusicVid']),
                    'Label': mvid['strTrack']}
            mvids.append(mvid)
    else:
        log("Error when handling HandleAudioDBMusicVideoResult results")
    return mvids


def GetExtendedAudioDBInfo(results):
    artists = []
    if 'artists' in results and results['artists']:
        for artist in results['artists']:
            localbio = 'strBiography' + __addon__.getSetting("LanguageID").upper()
            if localbio in artist and artist[localbio] is not None:
                Description = artist.get(localbio, "")
            elif 'strBiographyEN' in artist and artist['strBiographyEN'] is not None:
                Description = artist.get('strBiographyEN', "")
            elif 'strBiography' in artist:
                Description = artist.get('strBiography', "")
            else:
                Description = ""
            if 'strArtistBanner' in artist and artist['strArtistBanner'] is not None:
                banner = artist['strArtistBanner']
            else:
                banner = ""
            if "strReview" in artist:
                Description += "[CR]" + artist.get('strReview', "")
            artist = {'artist': artist.get('strArtist', ""),
                      'mbid': artist.get('strMusicBrainzID', ""),
                      'Banner': banner,
                      'Logo': artist.get('strArtistLogo', ""),
                      'Fanart': artist.get('strArtistFanart', ""),
                      'Fanart2': artist.get('strArtistFanart2', ""),
                      'Fanart3': artist.get('strArtistFanart3', ""),
                      'Born': artist.get('intBornYear', ""),
                      'Formed': artist.get('intFormedYear', ""),
                      'Died': artist.get('intDiedYear', ""),
                      'Disbanded': artist.get('intDiedYear', ""),
                      'Mood': artist.get('strMood', ""),
                      'Artist_Born': artist.get('intBornYear', ""),
                      'Artist_Formed': artist.get('intFormedYear', ""),
                      'Artist_Died': artist.get('intDiedYear', ""),
                      'Artist_Disbanded': artist.get('strDisbanded', ""),
                      'Artist_Mood': artist.get('strMood', ""),
                      'Country': artist.get('strCountryCode', ""),
                      'CountryName': artist.get('strCountry', ""),
                      'Website': artist.get('strWebsite', ""),
                      'Twitter': artist.get('strTwitter', ""),
                      'Facebook': artist.get('strFacebook', ""),
                      'LastFMChart': artist.get('strLastFMChart', ""),
                      'Gender': artist.get('strGender', ""),
                      'audiodbid': artist.get('idArtist', ""),
                      'Description': Description,
                      'Plot': Description,
                      'Path': "",
                      'Genre': artist.get('strSubGenre', ""),
                      'Style': artist.get('strGenre', ""),
                      'Label2': artist.get('strSubGenre', ""),
                      'Thumb': artist.get('strArtistThumb', ""),
                      'Art(Thumb)': artist.get('strArtistThumb', ""),
                      'Members': artist.get('intMembers', "")}
            artists.append(artist)
    else:
        log("Error when handling GetExtendedAudioDBInfo results")
    if len(artists) > 0:
        return artists[0]
    else:
        return {}


def GetDiscography(search_string):
    url = 'searchalbum.php?s=%s' % (urllib.quote_plus(search_string))
    results = Get_JSON_response(base_url + url)
    return HandleAudioDBAlbumResult(results)


def GetArtistDetails(search_string):
    url = 'search.php?s=%s' % (urllib.quote_plus(search_string))
    results = Get_JSON_response(base_url + url)
   # prettyprint(results)
    return GetExtendedAudioDBInfo(results)


def GetMostLovedTracks(search_string="", mbid=""):
    if mbid:
        pass
    else:
        url = 'track-top10.php?s=%s' % (urllib.quote_plus(search_string))
    log("GetMostLoveTracks URL:" + url)
    results = Get_JSON_response(base_url + url)
    return HandleAudioDBTrackResult(results)


def GetAlbumDetails(audiodbid="", mbid=""):
    if audiodbid:
        url = 'album.php?m=%s' % (audiodbid)
    elif mbid:
        url = 'album-mb.php?i=%s' % (mbid)
    results = Get_JSON_response(base_url + url)
  #  prettyprint(results)
    return HandleAudioDBAlbumResult(results)[0]


def GetMusicVideos(audiodbid):
    if audiodbid:
        url = 'mvid.php?i=%s' % (audiodbid)
        results = Get_JSON_response(base_url + url)
        return HandleAudioDBMusicVideoResult(results)
    else:
        return []


def GetTrackDetails(audiodbid):
    if audiodbid:
        url = 'track.php?m=%s' % (audiodbid)
        results = Get_JSON_response(base_url + url)
        return HandleAudioDBTrackResult(results)
    else:
        return []
