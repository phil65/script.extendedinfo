import xml.dom.minidom
from Utils import log, GetStringFromUrl, GetValue

lastfm_apikey = 'fbd57a1baddb983d1848a939665310f6'

def GetSimilarById(m_id):
    url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&mbid=%s&api_key=%s' % (m_id, lastfm_apikey)
    ret = GetStringFromUrl(url)
    
    curXML = xml.dom.minidom.parseString(ret)
    
    curXMLs = curXML.getElementsByTagName('lfm')
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