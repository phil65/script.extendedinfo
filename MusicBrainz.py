import xbmc, xbmcgui, urllib, re, xml.dom.minidom, time
from Utils import log, GetStringFromUrl, GetValue, GetAttribute
'''
def GetMusicBrainzId(artist):
    xbmc.executehttpapi( "SetResponseFormat()" )
    xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
    xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )
    xbmc.executehttpapi('')
    
    sqlQuery = "SELECT DISTINCT artist.strArtist, song.idArtist, song.strMusicBrainzArtistID FROM song JOIN artist ON artist.idArtist=song.idArtist WHERE artist.strArtist='%s'" %artist
    results = xbmc.executehttpapi( "QueryMusicDatabase(%s)" % urllib.quote_plus( sqlQuery ) )
    records = re.findall( "<record>(.+?)</record>", results, re.DOTALL )
    
    if len(records) == 1:
        fields = re.findall( "<field>(.+?)</field>", records[0], re.DOTALL)
        
        if len(fields) == 3:
            if fields[2] == 'not_there':
                log('We searched MusicBrainz before and not found - let\'s try again')
                return GetMusicBrainzIdFromNet(artist, int(fields[1]))
            else:
                log('MusicBrainz id is already stored in XBMC database')
                return fields[2]
        else:
            log('We didn\'t search MusicBrainz for this artist yet - let\'s try')
            return GetMusicBrainzIdFromNet(artist, int(fields[1]))
    
    
    return None
'''
def GetMusicBrainzId(artist):
    # todo: get mbid by using JSON
    records=[]
    if len(records) == 1:
        fields = re.findall( "<field>(.+?)</field>", records[0], re.DOTALL)
        
        if len(fields) == 3:
            if fields[2] == 'not_there':
                log('We searched MusicBrainz before and not found - let\'s try again')
                return GetMusicBrainzIdFromNet(artist, int(fields[1]))
            else:
                log('MusicBrainz id is already stored in XBMC database')
                return fields[2]
        else:
            log('We didn\'t search MusicBrainz for this artist yet - let\'s try')
            return GetMusicBrainzIdFromNet(artist, int(fields[1]))
    
    
    return None


def GetMusicBrainzIdFromNet(artist, xbmc_artist_id = -1):
    url = 'http://musicbrainz.org/ws/1/artist/?type=xml&name=%s' % urllib.quote_plus(artist)
    
    tries = 0
    trylimit = 5
    gotit = False
    while tries < trylimit and not gotit:
        ret = GetStringFromUrl(url)
        
        if 'requests are exceeding the allowable rate limit' in ret:
            log('MusicBrainz limits amount of request per time - we must wait')
            time.sleep(1)
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
    # OR song.idArtist='SELECT' <- total workaround to force execution of sql query
    # xbmc allows only queries with SELECT phrase
    update_query = "UPDATE song SET strMusicBrainzArtistID='%s' WHERE idArtist=%i OR strMusicBrainzArtistID='SELECT'" % (musicbrainz_id, xbmc_artist_id)
    xbmc.executehttpapi("QueryMusicDatabase(%s)" % urllib.quote_plus( update_query ) )

def SetMusicBrainzIDsForAllArtists(Progress, CheckForNotFound):
    #TODO - maybe add notification on start and end - ofcourse can be disabled

    xbmc.executehttpapi( "SetResponseFormat()" )
    xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
    xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )
    xbmc.executehttpapi('')
    
    if CheckForNotFound:
        sqlQuery = "SELECT artist.strArtist, song.idArtist, song.strMusicBrainzArtistID FROM song JOIN artist ON artist.idArtist=song.idArtist WHERE song.strMusicBrainzArtistID='' OR song.strMusicBrainzArtistID='not_there' GROUP BY song.idArtist"
    else:
        sqlQuery = "SELECT artist.strArtist, song.idArtist, song.strMusicBrainzArtistID FROM song JOIN artist ON artist.idArtist=song.idArtist WHERE song.strMusicBrainzArtistID='' GROUP BY song.idArtist"
    
    results = xbmc.executehttpapi( "QueryMusicDatabase(%s)" % urllib.quote_plus( sqlQuery ) )
    records = re.findall( "<record>(.+?)</record>", results, re.DOTALL )
    
    if Progress:
        progressDialog = xbmcgui.DialogProgress('Updating Music Database with MusicBrainz IDs for artists')
        progressDialog.create('Updating Music Database with MusicBrainz IDs for artists')
    
    for count, record in enumerate(records):
        fields = re.findall( "<field>(.*?)</field>", record, re.DOTALL )
        
        if Progress:
            if progressDialog.iscanceled():
                return
            
            progressDialog.update( (count * 100) / len(records)  , 'Updating: %s' % fields[0])

        brainz_id = -1
        xbmc_id = int(fields[1])
        
        while brainz_id == -1: #ensure we got response
            if Progress and progressDialog.iscanceled():
                return
            
            brainz_id = GetMusicBrainzIdFromNet(fields[0], xbmc_id)
            
        if brainz_id == None:
            SetMusicBrainzID(xbmc_id, 'not_there')
                