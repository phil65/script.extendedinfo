import xbmc, urllib, xml.dom.minidom
from Utils import log, GetStringFromUrl, GetValue, GetAttribute

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

def GetMusicBrainzIdFromNet(artist, xbmc_artist_id = -1):
    url = 'http://musicbrainz.org/ws/1/artist/?type=xml&name=%s' % urllib.quote_plus(artist)
    tries = 0
    trylimit = 5
    gotit = False
    while tries < trylimit and not gotit:
        ret = GetStringFromUrl(url)
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
    artistName = GetValue(curXML, 'name') 
    artistMusicBrainzId = curXML.getAttribute('id')
    log('Found MusicBrainz ID')
    if xbmc_artist_id != -1:
        SetMusicBrainzID(xbmc_artist_id, artistMusicBrainzId)
    return artistMusicBrainzId

def SetMusicBrainzID(xbmc_artist_id,musicbrainz_id):
    pass
    #todo: set MBID with JSON if possible

def SetMusicBrainzIDsForAllArtists(Progress, CheckForNotFound):
    #TODO - same as above
    pass
    # if Progress:
        # progressDialog = xbmcgui.DialogProgress('Updating Music Database with MusicBrainz IDs for artists')
        # progressDialog.create('Updating Music Database with MusicBrainz IDs for artists')
    # for count, record in enumerate(records):
        # fields = re.findall( "<field>(.*?)</field>", record, re.DOTALL )
        # if Progress:
            # if progressDialog.iscanceled():
                # return
            # progressDialog.update( (count * 100) / len(records)  , 'Updating: %s' % fields[0])
        # brainz_id = -1
        # xbmc_id = int(fields[1])
        # while brainz_id == -1: #ensure we got response
            # if Progress and progressDialog.iscanceled():
                # return
            # brainz_id = GetMusicBrainzIdFromNet(fields[0], xbmc_id)            
        # if brainz_id == None:
            # SetMusicBrainzID(xbmc_id, 'not_there')
                