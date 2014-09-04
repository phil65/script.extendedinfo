import xbmc
import urllib
import xml.dom.minidom
import xbmcaddon
import os
import xbmcvfs
import time
from Utils import GetStringFromUrl, log, read_from_file
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))


# def artist_musicbrainz_id( artist_id, artist_mbid ):
    # artist_details = retrieve_artist_details( artist_id )
    # artist = []
    # if not artist_details["musicbrainzartistid"] or not artist_mbid:
        # name, artist["musicbrainz_artistid"], sortname = get_musicbrainz_artist_id( get_unicode( artist_details["label"] ) )
        # artist[ "name" ] = get_unicode( artist_details[ "label" ] )
    # else:
        # artist[ "name" ] = get_unicode( artist_details["label"] )
        # if artist_mbid:
            # artist[ "musicbrainz_artistid" ] = artist_mbid
        # else:
            # artist[ "musicbrainz_artistid" ] = artist_details["musicbrainzartistid"]
    # return artist

def GetAttribute(node, attr):
    v = unicode(node.getAttribute(tag))


def GetValue(node, tag):
    v = node.getElementsByTagName(tag)
    if len(v) == 0:
        return '-'
    if len(v[0].childNodes) == 0:
        return '-'
    return unicode(v[0].childNodes[0].data)


def GetMusicBrainzIdFromNet(artist, xbmc_artist_id=-1):
    import base64
    url = 'http://musicbrainz.org/ws/1/artist/?type=xml&name=%s' % urllib.quote_plus(artist)
    tries = 0
    trylimit = 5
    gotit = False
    filename = base64.urlsafe_b64encode(url)
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        return read_from_file(filename)
    else:
        while tries < trylimit and not gotit:
            ret = GetStringFromUrl(url)
            if ret:
                if 'requests are exceeding the allowable rate limit' in ret:
                    log('MusicBrainz limits amount of request per time - we must wait')
                    xbmc.sleep(1000)
                    tries = tries + 1
                else:
                    gotit = True
        if not gotit:
            return -1
        curXML = xml.dom.minidom.parseString(ret)
        curXMLs = curXML.getElementsByTagName('metadata')
        if len(curXMLs) > 0:
            curXML = curXMLs[0]
        else:
            return None
        curXMLs = curXML.getElementsByTagName('artist-list')
        if len(curXMLs) > 0:
            curXML = curXMLs[0]
        else:
            return None
        curXMLs = curXML.getElementsByTagName('artist')
        if len(curXMLs) > 0:
            curXML = curXMLs[0]
        else:
            return None
      #  artistName = GetValue(curXML, 'name')
        artistMusicBrainzId = curXML.getAttribute('id')
        log('Found MusicBrainz ID')
    #    if xbmc_artist_id != -1:
    #        SetMusicBrainzID(xbmc_artist_id, artistMusicBrainzId)
        return artistMusicBrainzId
