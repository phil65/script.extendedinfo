import urllib, xml.dom.minidom, xbmc, xbmcaddon,xbmcgui
import os,sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__language__     = __addon__.getLocalizedString

Window = 10000

def AddArtToLibrary( type, media, folder, limit , silent = False):
    import xbmcvfs
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%ss", "params": {"properties": ["art", "file"], "sort": { "method": "label" } }, "id": 1}' % media.lower())
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if (json_response['result'] != None) and (json_response['result'].has_key('%ss' % media.lower())):
        # iterate through the results
        if silent == False:
            progressDialog = xbmcgui.DialogProgress(__language__(32016))
            progressDialog.create(__language__(32016))
        for count,item in enumerate(json_response['result']['%ss' % media.lower()]):
            if silent == False:
                if progressDialog.iscanceled():
                    return
            path= media_path(item['file']).encode("utf-8") + "/" + folder + "/"
            file_list = xbmcvfs.listdir(path)[1]            
            for i,file in enumerate (file_list):
                if i + 1 > limit:
                    break
                if silent == False:
                    progressDialog.update( (count * 100) / json_response['result']['limits']['total']  , __language__(32011) + ' %s: %s %i' % (item["label"],type,i + 1))
                    if progressDialog.iscanceled():
                        return
                file_path =  path + "/" + file
                log(file_path)
                if xbmcvfs.exists(file_path) and item['art'].get('%s%i' % (type,i),'') == "" :
                    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Set%sDetails", "params": { "%sid": %i, "art": { "%s%i": "%s" }}, "id": 1 }' %( media , media.lower() , item.get('%sid' % media.lower()) , type , i + 1, file_path))

def import_skinsettings():
    importstring=read_from_file()
    if importstring:
        progressDialog = xbmcgui.DialogProgress(__language__(32010))
        progressDialog.create(__language__(32010))
        xbmc.sleep(200)
        for count, skinsetting in enumerate(importstring):
            if progressDialog.iscanceled():
                return
            if skinsetting[1].startswith(xbmc.getSkinDir()):
                progressDialog.update( (count * 100) / len(importstring)  , __language__(32011) + ' %s' % skinsetting[1])
                setting = skinsetting[1].replace(xbmc.getSkinDir() + ".","")
                if skinsetting[0] == "string":
                    if skinsetting[2] <> "":
                        xbmc.executebuiltin( "Skin.SetString(%s,%s)" % (setting,skinsetting[2]) )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" % setting )
                elif skinsetting[0] == "bool":
                    if skinsetting[2] == "true":
                        xbmc.executebuiltin( "Skin.SetBool(%s)" % setting )
                    else:
                        xbmc.executebuiltin( "Skin.Reset(%s)" % setting )
            xbmc.sleep(30)
        xbmcgui.Dialog().ok(__language__(32005),__language__(32009))
    else:
        log("backup not found")

def export_skinsettings():
    import xbmcvfs
    from xml.dom.minidom import parse
    # Set path
    guisettings_path = xbmc.translatePath( 'special://profile/guisettings.xml' ).decode("utf-8")
    # Check to see if file exists
    if xbmcvfs.exists( guisettings_path ):
        log("guisettings.xml found")
        doc = parse( guisettings_path )
        skinsettings = doc.documentElement.getElementsByTagName( 'setting' )
        newlist = []
        for count, skinsetting in enumerate(skinsettings):
            if skinsetting.childNodes:
                value = skinsetting.childNodes [ 0 ].nodeValue
            else:
                value = ""
            if skinsetting.attributes[ 'name' ].nodeValue.startswith(xbmc.getSkinDir()):
                newlist.append((skinsetting.attributes[ 'type' ].nodeValue,skinsetting.attributes[ 'name' ].nodeValue,value))
        if save_to_file(newlist,"backup"):
            xbmcgui.Dialog().ok(__language__(32005),__language__(32006))
    else:
        xbmcgui.Dialog().ok(__language__(32007),__language__(32008))
        log("guisettings.xml not found")

def GetXBMCArtists():
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["genre", "description", "mood", "style", "born", "died", "formed", "disbanded", "yearsactive", "instrument", "fanart", "thumbnail", "musicbrainzartistid"]}, "id": 1}')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = simplejson.loads(json_query)
    artists = []        
    if json_query.has_key('result') and json_query['result'].has_key('artists'):
        count = 0
        for item in json_query['result']['artists']:
            mbid = ''
            artist = {"Title": item['label'],
                      "DBID": item['artistid'],
                      "mbid": item['musicbrainzartistid'] ,
                      "Art(thumb)": item['thumbnail'] ,
                      "Art(fanart)": item['fanart'] ,
                      "description": item['description'] ,
                      "Born": item['born'] ,
                      "Died": item['died'] ,
                      "Formed": item['formed'] ,
                      "Disbanded": item['disbanded'] ,
                      "YearsActive": " / ".join(item['yearsactive']) ,
                      "Style": " / ".join(item['style']) ,
                      "Mood": " / ".join(item['mood']) ,
                      "Instrument": " / ".join(item['instrument']) ,
                      "Genre": " / ".join(item['genre']) ,
                      "LibraryPath": 'musicdb://2/' + str(item['artistid']) + '/'
                      }
            artists.append(artist)
    return artists

def media_path(path):
    # Check for stacked movies
    try:
        path = os.path.split(path)[0].rsplit(' , ', 1)[1].replace(",,",",")
    except:
        path = os.path.split(path)[0]
    # Fixes problems with rared movies and multipath
    if path.startswith("rar://"):
        path = [os.path.split(urllib.url2pathname(path.replace("rar://","")))[0]]
    elif path.startswith("multipath://"):
        temp_path = path.replace("multipath://","").split('%2f/')
        path = []
        for item in temp_path:
            path.append(urllib.url2pathname(item))
    else:
        path = [path]
    return path[0]
    
def GetStringFromUrl(encurl):
    doc = ""
    succeed = 0
    while succeed < 5:
        try: 
            f = urllib.urlopen(  encurl)
            doc = f.read()
            f.close()
            return str(doc)
        except:
            log("could not get data from %s" % encurl)
            succeed = succeed + 1

def GetValue(node, tag):
    v = node.getElementsByTagName(tag)
    if len(v) == 0:
        return '-'
    
    if len(v[0].childNodes) == 0:
        return '-'
    
    return unicode(v[0].childNodes[0].data)
    
def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

def GetAttribute(node, attr):
    v = unicode(node.getAttribute(tag))

def get_browse_dialog( default="", heading="", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value
    
def save_to_file(content, suffix, path = "" ):
    try:
        if path == "":
            text_file_path = get_browse_dialog() + xbmc.getSkinDir() +"." + suffix + ".txt"
        else:
            if not xbmcvfs.exists(path):
                xbmcvfs.mkdir(path)
            text_file_path = path + xbmc.getSkinDir() +"." + suffix + ".txt"
        log("text_file_path:")
        log(text_file_path)
        text_file =  open(text_file_path, "w")
        simplejson.dump(content,text_file)
        text_file.close()
        return True
    except Exception,e:
        log(e)
        return False
        
def read_from_file(path = "" ):
    import xbmcvfs
    # Set path
    backup_path = get_browse_dialog(dlg_type=1)
    # Check to see if file exists
    if xbmcvfs.exists( backup_path ):
        with open(backup_path) as f: fc = simplejson.load(f)
        return fc
    else:
        return False

def ConvertYoutubeURL(string):
    import re
    if 'youtube.com/v' in string:
        vid_ids = re.findall('http://www.youtube.com/v/(.{11})\??', string, re.DOTALL )
        for id in vid_ids:
            convertedstring = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return convertedstring       
    if 'youtube.com/watch' in string:
        vid_ids = re.findall('youtube.com/watch\?v=(.{11})\??', string, re.DOTALL )       
        for id in vid_ids:
            convertedstring = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return convertedstring    
    return ""
    
def ExtractYoutubeID(string):
    import re
    if 'youtube.com/v' in string:
        vid_ids = re.findall('http://www.youtube.com/v/(.{11})\??', string, re.DOTALL )
        for id in vid_ids:
            return id       
    if 'youtube.com/watch' in string:
        vid_ids = re.findall('youtube.com/watch\?v=(.{11})\??', string, re.DOTALL )       
        for id in vid_ids:
            return id    
    return ""
   
def Notify(header, line='', line2='', line3=''):
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % (header, line, line2, line3) )
    
def passDataToSkin(prefix, data):
    #use window properties       
    wnd = xbmcgui.Window(Window)
   # for i in range(1,100):
    #   for schleife zum resetten evtl
     #  wnd.setProperty('%s.%i.%s' % (prefix, count + 1, str(key)), unicode(value))
    if data != None:
        wnd.setProperty('%s.Count' % prefix, str(len(data)))
    #    log( "%s.Count = %s" % (prefix, str(len(data)) ) )
        for (count, result) in enumerate(data):
   #         log( "%s.%i = %s" % (prefix, count + 1, str(result) ) )
            for (key,value) in result.iteritems():
                wnd.setProperty('%s.%i.%s' % (prefix, count + 1, str(key)), unicode(value))
     #           log('%s.%i.%s' % (prefix, count + 1, str(key)) + unicode(value))
    else:
        wnd.setProperty('%s.Count' % prefix, '0')