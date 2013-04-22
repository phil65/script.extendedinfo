import urllib, xml.dom.minidom, xbmc, xbmcaddon,xbmcgui,xbmcvfs,datetime
import os,sys,time
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__language__     = __addon__.getLocalizedString
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % __addonid__ ).decode("utf-8") )

Window = 10000
locallist = []

def string2deg(string):
    import re
    string = string.strip() # trim leading/trailing whitespace
    string = string.replace('"','')
    string = string.replace("'","")
    if string[0].lower() == "w" or string[0].lower() == "s":
       negative = True
    else:
        negative = False
    string = string[1:]
    string = string.replace("d","")
    string = string.replace("  "," ")
    div = '[|:|\s]' # allowable field delimiters "|", ":", whitespace
    sdec = '(\d{1,3})' + div + '(\d{1,2})' + div + '(\d{1,2}\.?\d+?)'
    co_re= re.compile(sdec)
    co_search= co_re.search(string)
    if co_search is None:
        raise ValueError("Invalid input string: %s" % string)
    elems = co_search.groups()
    degrees = float(elems[0])
    arcminutes = float(elems[1])
    arcseconds = float(elems[2])
    decDegrees = degrees + arcminutes/60.0 + arcseconds/3600.0
    if negative:
        decDegrees = -1.0 * decDegrees
    return decDegrees


def AddArtToLibrary( type, media, folder, limit , silent = False):
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
    importstring = read_from_file()
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
        if save_to_file(newlist,xbmc.getSkinDir() + ".backup"):
            xbmcgui.Dialog().ok(__language__(32005),__language__(32006))
    else:
        xbmcgui.Dialog().ok(__language__(32007),__language__(32008))
        log("guisettings.xml not found")

        
def create_musicvideo_list():
    musicvideos = []
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["artist", "file"], "sort": { "method": "artist" } }, "id": 1}')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if (json_response['result'] != None) and (json_response['result'].has_key('musicvideos')):
        # iterate through the results
        for item in json_response['result']['musicvideos']:
            artist = item['artist']
            title = item['label']
            path = item['file']
            musicvideos.append((artist,title,path))
        return musicvideos
    else:
        return False
        
def create_movie_list():
    movies = []
    filename = Addon_Data_Path + "/XBMCmovies.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        return read_from_file(filename)
    else:
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["year", "file", "art", "genre", "director","cast","studio","country","tag"], "sort": { "method": "label" } }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        save_to_file(json_query,"XBMCmovies",Addon_Data_Path)
        json_response = simplejson.loads(json_query)
        if (json_response['result'] != None) and (json_response['result'].has_key('movies')):
            # iterate through the results
            for item in json_response['result']['movies']:
                year = item['year']
                DBID = item['id']
                path = item['file']
                art = item['art']
                genre = item['genre']
                director = item['director']
                cast = item['cast']
                studio = item['studio']
                country = item['country']
                tag = item['tag']
                movies.append((year,path,art,genre,director,cast,studio,country,tag))
            return movies
        else:
            return False
            
            
def create_light_movielist():
    movies = []
    filename = Addon_Data_Path + "/XBMClightmovielist.txt"
    # if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 1:
        # return read_from_file(filename)
    if True:
        a = datetime.datetime.now()
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["set", "originaltitle", "streamdetails", "imdbnumber", "file"], "sort": { "method": "label" } }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query = simplejson.loads(json_query)
        save_to_file(json_query,"XBMClightmovielist",Addon_Data_Path)
        b = datetime.datetime.now() - a
        log('Processing Time for creating light movielist: %s' % b)
        return json_query
            
def media_streamdetails(filename, streamdetails):
    info = {}
    video = streamdetails['video']
    audio = streamdetails['audio']
    if '3d' in filename:
        info['videoresolution'] = '3d'
    elif video:
        videowidth = video[0]['width']
        videoheight = video[0]['height']
        if (video[0]['width'] <= 720 and video[0]['height'] <= 480):
            info['videoresolution'] = "480"
        elif (video[0]['width'] <= 768 and video[0]['height'] <= 576):
            info['videoresolution'] = "576"
        elif (video[0]['width'] <= 960 and video[0]['height'] <= 544):
            info['videoresolution'] = "540"
        elif (video[0]['width'] <= 1280 and video[0]['height'] <= 720):
            info['videoresolution'] = "720"
        elif (video[0]['width'] >= 1281 or video[0]['height'] >= 721):
            info['videoresolution'] = "1080"
        else:
            info['videoresolution'] = ""
    elif (('dvd') in filename and not ('hddvd' or 'hd-dvd') in filename) or (filename.endswith('.vob' or '.ifo')):
        info['videoresolution'] = '576'
    elif (('bluray' or 'blu-ray' or 'brrip' or 'bdrip' or 'hddvd' or 'hd-dvd') in filename):
        info['videoresolution'] = '1080'
    else:
        info['videoresolution'] = '1080'
    if video:
        info['videocodec'] = video[0]['codec']
        if (video[0]['aspect'] < 1.4859):
            info['videoaspect'] = "1.33"
        elif (video[0]['aspect'] < 1.7190):
            info['videoaspect'] = "1.66"
        elif (video[0]['aspect'] < 1.8147):
            info['videoaspect'] = "1.78"
        elif (video[0]['aspect'] < 2.0174):
            info['videoaspect'] = "1.85"
        elif (video[0]['aspect'] < 2.2738):
            info['videoaspect'] = "2.20"
        else:
            info['videoaspect'] = "2.35"
    else:
        info['videocodec'] = ''
        info['videoaspect'] = ''
    if audio:
        info['audiocodec'] = audio[0]['codec']
        info['audiochannels'] = audio[0]['channels']
    else:
        info['audiocodec'] = ''
        info['audiochannels'] = ''
    return info



            
def GetXBMCArtists():
    artists = []        
    filename = Addon_Data_Path + "/XBMCartists.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        return read_from_file(filename)
    else:
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["genre", "description", "mood", "style", "born", "died", "formed", "disbanded", "yearsactive", "instrument", "fanart", "thumbnail", "musicbrainzartistid"]}, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        save_to_file(json_query,"XBMCartists",Addon_Data_Path)
        json_query = simplejson.loads(json_query)
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
    
def GetXBMCAlbums():
    albums = []        
    filename = Addon_Data_Path + "/XBMCalbums.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        return read_from_file(filename)
    else:
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["title", "description", "albumlabel", "theme", "mood", "style", "type", "artist", "genre", "year", "thumbnail", "fanart", "rating", "playcount", "musicbrainzartistid"]}, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        save_to_file(json_query,"XBMCalbums",Addon_Data_Path)
        json_query = simplejson.loads(json_query)
        if json_query.has_key('result') and json_query['result'].has_key('albums'):
            count = 0
            for item in json_query['result']['albums']:
                mbid = ''
                album = {"Title": item['label'],
                          "DBID": item['albumid'],
                          "Artist": item['artist'],
                          "mbid": item['musicbrainzartistid'] ,
                          "Art(thumb)": item['thumbnail'] ,
                          "Art(fanart)": item['fanart'] ,
                          "Description": item['description'] ,
                          "Rating": item['rating'] ,
                          "RecordLabel": item['albumlabel'] ,
                          "Year": item['year'] ,
                          "YearsActive": " / ".join(item['yearsactive']) ,
                          "Style": " / ".join(item['style']) ,
                          "Type": " / ".join(item['type']) ,
                          "Mood": " / ".join(item['mood']) ,
                          "Theme": " / ".join(item['theme']) ,
                          "Genre": " / ".join(item['genre']) ,
                          "Play": 'XBMC.RunScript(script.playalbum,albumid=' + str(item.get('albumid')) + ')'
                          }
                albums.append(album)
        return albums
    
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

def CompareWithLibrary(onlinelist):
    global locallist
    if not locallist:
        locallist = create_light_movielist()
        log("movielist created")
    a = datetime.datetime.now()
    log("startin compare")
    for onlineitem in onlinelist:
        for localitem in locallist["result"]["movies"]:
            comparators = [localitem["originaltitle"],localitem["label"]]
            if onlineitem["OriginalTitle"] in comparators:
                streaminfo = media_streamdetails(localitem['file'].encode('utf-8').lower(), localitem['streamdetails'])
                log("compare success" + onlineitem["Title"])
                log(localitem)
                onlineitem.update({"Play": localitem["movieid"]})             
                onlineitem.update({"DBID": localitem["movieid"]})             
                onlineitem.update({"VideoCodec": streaminfo["videocodec"]})             
                onlineitem.update({"VideoResolution": streaminfo["videoresolution"]})             
                onlineitem.update({"VideoAspect": streaminfo["videoaspect"]})             
                onlineitem.update({"AudioCodec": streaminfo["audiocodec"]})             
                onlineitem.update({"AudioChannels": str(streaminfo["audiochannels"])})
                break
    b = datetime.datetime.now() - a
    log('Processing Time for comparing: %s' % b)
    return onlinelist

    
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
            xbmc.sleep(1000)
            succeed += 1
    return ""

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
        
def save_to_file(content, filename, path = "" ):
    import xbmcvfs
    if True:
        if path == "":
            text_file_path = get_browse_dialog() + filename + ".txt"
        else:
            if not xbmcvfs.exists(path):
                xbmcvfs.mkdir(path)
            text_file_path = os.path.join(path,filename + ".txt")
        log("save to textfile:")
        log(text_file_path)
        text_file =  open(text_file_path, "w")
        simplejson.dump(content,text_file)
        text_file.close()
        return True
    else:
        return False
        
def read_from_file(path = "" ):
    import xbmcvfs
    log("trying to load " + path)
    # Set path
    if path == "":
        path = get_browse_dialog(dlg_type=1)
    # Check to see if file exists
    if xbmcvfs.exists( path ):
        with open(path) as f: fc = simplejson.load(f)
        log("loaded textfile " + path)
        if True:
            return fc
        else:
            log("error when loading file")
            log(fc)
            return []
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
 
def GetDatabaseID(type,dbid):
    if type=="movie":
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["imdbnumber","title", "year"], "movieid":%s }, "id": 1}' % dbid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if json_response['result'].has_key('moviedetails'):
            return json_response['result']['moviedetails']['imdbnumber']
        else:
            return []
    elif type == "tvshow":
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"properties": ["imdbnumber","title", "year"], "tvshowid":%s }, "id": 1}' % dbid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if json_response['result'].has_key('tvshowdetails'):
            return json_response['result']['tvshowdetails']['imdbnumber']
        else:
            return []
            
            
def GetMovieSetName(dbid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["setid"], "movieid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if json_response['result'].has_key('moviedetails'):
        dbsetid = json_response['result']['moviedetails'].get('setid',"")
        if dbsetid:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid":%s }, "id": 1}' % dbsetid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = simplejson.loads(json_query)
            return json_response['result']['setdetails'].get('label',"")
    return ""    

def getCacheThumbName(url, CachePath):
    thumb = xbmc.getCacheThumbName(url)
    thumbpath = os.path.join(CachePath, thumb)
    return thumbpath

def cleanText(text):
    import re
    text = re.sub('<br \/>','[CR]',text)
    text = re.sub('<(.|\n|\r)*?>','',text)
    text = re.sub('&quot;','"',text)
    text = re.sub('&amp;','&',text)
    text = re.sub('&gt;','>',text)
    text = re.sub('&lt;','<',text)
    text = re.sub('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.','',text)
    return text.strip()

def download(src, dst, dst2):
    if (not xbmc.abortRequested):
        tmpname = xbmc.translatePath('special://profile/addon_data/%s/temp/%s' % ( __addonname__ , xbmc.getCacheThumbName(src) )).decode("utf-8")
        if xbmcvfs.exists(tmpname):
            xbmcvfs.delete(tmpname)
        urllib.urlretrieve( src, tmpname )
        if os.path.getsize(tmpname) > 999:
            log( 'copying file to transition directory' )
            xbmcvfs.copy(tmpname, dst2)
            log( 'moving file to cache directory' )
            xbmcvfs.rename(tmpname, dst)
        else:
            xbmcvfs.delete(tmpname)

def passHomeDataToSkin(data, debug = True):
    wnd = xbmcgui.Window(Window)
    if data != None:
        for (key,value) in data.iteritems():
            wnd.setProperty('%s' % (str(key)), unicode(value))
            if debug:
                log('%s' % (str(key)) + unicode(value))
    
            
def passDataToSkin(name, data, prefix="",debug = False):
    wnd = xbmcgui.Window(Window)
    if data != None:
        if debug:
            log( "%s%s.Count = %s" % (prefix, name, str(len(data)) ) )
        for (count, result) in enumerate(data):
            if debug:
                log( "%s%s.%i = %s" % (prefix, name, count + 1, str(result) ) )
            for (key,value) in result.iteritems():
                wnd.setProperty('%s%s.%i.%s' % (prefix, name, count + 1, str(key)), unicode(value))
                if debug:
                    log('%s%s.%i.%s' % (prefix, name, count + 1, str(key)) + unicode(value))
        wnd.setProperty('%s%s.Count' % (prefix, name), str(len(data)))
    else:
        wnd.setProperty('%s%s.Count' % (prefix, name), '0')
        
def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))