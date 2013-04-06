import sys
import os, time, datetime, re, random
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, xbmcvfs
from Utils import GetStringFromUrl, log, media_path,get_browse_dialog
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__     = __addon__.getLocalizedString

infos = []
Artist_mbid = None
AlbumName = None
TrackTitle = None
AdditionalParams = []
Window = 10000
extrathumb_limit = 4
extrafanart_limit = 10
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % __addonid__ ).decode("utf-8") )
Skin_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmc.getSkinDir() ).decode("utf-8") )


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

def GetXBMCArtists():
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["musicbrainzartistid", "thumbnail"]}, "id": 1}')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    log(json_query)
    json_query = simplejson.loads(json_query)
    artists = []        
    if json_query.has_key('result') and json_query['result'].has_key('artists'):
        count = 0
        for item in json_query['result']['artists']:
            mbid = ''
            artist = {"name": item['label'], "xbmc_id": item['artistid'], "mbid": item['musicbrainzartistid'] , "thumb": item['thumbnail'] }
            artists.append(artist)
    return artists

def GetXKCDInfo():
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    for i in range(0,10):
        try:
            url = 'http://xkcd.com/%i/info.0.json' % random.randrange(1, 1190)
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
            wnd = xbmcgui.Window(Window)
            wnd.setProperty('XKCD.%i.Image' % i, results["img"])
            wnd.setProperty('XKCD.%i.Title' % i, results["title"])
            wnd.setProperty('XKCD.%i.Description' % i, results["alt"])
        except:
            log("Error when setting XKCD info")

def GetCandHInfo():
    count = 1
    for i in range(1,30):
        try:
            url = 'http://www.explosm.net/comics/%i/' % random.randrange(1, 3128)
            response = GetStringFromUrl(url)
        except:
            log("Error when fetching CandH data from net")
        if response:
            log(response)
            wnd = xbmcgui.Window(Window)
            regex = ur'src="([^"]+)"'
            matches = re.findall(regex, response)
            if matches:
                for item in matches:
                    if item.startswith('http://www.explosm.net/db/files/Comics/'):
                        wnd.setProperty('CyanideHappiness.%i.Image' % count, item)     
                        count += 1
             #   
              #  wnd.setProperty('CyanideHappiness.%i.Title' % count, item["title"])
                if count > 10:
                    break
                
def GetFlickrImages():
    results=[]
    try:
        url = 'http://pipes.yahoo.com/pipes/pipe.run?_id=241a9dca1f655c6fa0616ad98288a5b2&_render=json'
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching Flickr data from net")
    count = 1
    if results:
        wnd = xbmcgui.Window(Window)
        for item in results["value"]["items"]:
            wnd.setProperty('Flickr.%i.Background' % count, item["link"])
            count += 1
            

def ConvertYoutubeURL(string):        
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

            
def GetYoutubeVideos(jsonurl,prefix=""):
    results=[]
    if not prefix.endswith('.') and prefix <> "":
        prefix = prefix + '.'
    try:
        response = GetStringFromUrl(jsonurl)
        results = simplejson.loads(response)
    except:
        log("Error when fetching JSON data from net")
    count = 1
    if results:
        wnd = xbmcgui.Window(Window)
        for item in results["value"]["items"]:
            log("look here")
            log(item["media:thumbnail"][0]["url"])
            wnd.setProperty(prefix + 'RSS.%i.Thumb' % count, item["media:thumbnail"][0]["url"])
            wnd.setProperty(prefix + 'RSS.%i.Media' % count, ConvertYoutubeURL(item["link"]))
            wnd.setProperty(prefix + 'RSS.%i.Play' % count, "PlayMedia(" + ConvertYoutubeURL(item["link"]) + ")")
            wnd.setProperty(prefix + 'RSS.%i.Title' % count, item["title"])
            wnd.setProperty(prefix + 'RSS.%i.Description' % count, item["content"]["content"])
            wnd.setProperty(prefix + 'RSS.%i.Date' % count, item["pubDate"])
            count += 1
    
def GetSimilarInLibrary(id):
    from OnlineMusicInfo import GetSimilarById
    simi_artists = GetSimilarById(id)
    if simi_artists == None:
         log('Last.fm didn\'t return proper response')
         return None
    xbmc_artists = GetXBMCArtists()
    artists = []
    start = time.clock()
    for (count, simi_artist) in enumerate(simi_artists):
        for (count, xbmc_artist) in enumerate(xbmc_artists):
            hit = False
            if xbmc_artist['mbid'] != '':
                #compare music brainz id
                if xbmc_artist['mbid'] == simi_artist['mbid']:
                    hit = True
            else:
                #compare names
                if xbmc_artist['name'] == simi_artist['name']:
                    hit = True
            if hit:
                log('%s -> %s' % (xbmc_artist['name'], xbmc_artist['thumb']))
                artists.append(xbmc_artist)
    finish = time.clock()
    log('%i of %i artists found in last.FM is in XBMC database' % (len(artists), len(simi_artists)))
    return artists    

def passDataToSkin(prefix, data):
    #use window properties       
    wnd = xbmcgui.Window(Window)
   # for i in range(1,100):
    #   for schleife zum resetten evtl
     #  wnd.setProperty('%s.%i.%s' % (prefix, count + 1, str(key)), unicode(value))
    if data != None:
        wnd.setProperty('%s.Count' % prefix, str(len(data)))
        log( "%s.Count = %s" % (prefix, str(len(data)) ) )
        for (count, result) in enumerate(data):
            log( "%s.%i = %s" % (prefix, count + 1, str(result) ) )
            for (key,value) in result.iteritems():
                wnd.setProperty('%s.%i.%s' % (prefix, count + 1, str(key)), unicode(value))
                log('%s.%i.%s' % (prefix, count + 1, str(key)) + unicode(value))
    else:
        wnd.setProperty('%s.Count' % prefix, '0')

# def retrieve_artist_details( artist_id ):
    # json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtistDetails", "params": {"properties": ["musicbrainzartistid"], "artistid": %d}, "id": 1}' %artist_id)
    # json_query = unicode(json_query, 'utf-8', errors='ignore')
    # json_response = simplejson.loads(json_query)
    # if (json_response['result'] != None) and (json_response['result'].has_key('musicvideos')):       
    
def GetLastFMInfo():
    for info in infos:
        if info == 'xkcd':
            log("startin GetXKCDInfo")
            GetXKCDInfo()
        elif info == 'flickr':
            GetFlickrImages()
        elif info == 'cyanide':
            log("startin GetCandHInfo")
            GetCandHInfo()
        elif info == 'similarartistsinlibrary':
            artists = GetSimilarInLibrary(Artist_mbid)
            passDataToSkin('SimilarArtistsInLibrary', artists)
        elif info == 'artistevents':
            from OnlineMusicInfo import GetEvents
            events = GetEvents(Artist_mbid)
            passDataToSkin('ArtistEvents', events)       
        elif info == 'nearevents':
            from OnlineMusicInfo import GetNearEvents
            events = GetNearEvents()
            passDataToSkin('NearEvents', events)        
        elif info == 'topartistsnearevents':
            artists = GetXBMCArtists()
            events = GetArtistNearEvents(artists[0:15])
            passDataToSkin('TopArtistsNearEvents', events)
        elif info == 'updatexbmcdatabasewithartistmbidbg':
            from MusicBrainz import SetMusicBrainzIDsForAllArtists
            SetMusicBrainzIDsForAllArtists(False, 'forceupdate' in AdditionalParams)
        elif info == 'updatexbmcdatabasewithartistmbid':
            from MusicBrainz import SetMusicBrainzIDsForAllArtists
            SetMusicBrainzIDsForAllArtists(True, 'forceupdate' in AdditionalParams)
    
class Main:
    def __init__( self ):
        log("version %s started" % __addonversion__ )
        self._init_vars()
    #    GetYoutubeVideos("http://pipes.yahoo.com/pipes/pipe.run?_id=232e2f480431b82a9288a72778e2f1d4&_render=json&youtubeid=fional88","News")
        self._parse_argv()
        # run in backend if parameter was set
        if self.info:
            GetLastFMInfo()
        elif self.exportsettings:
            self._export_skinsettings()        
        elif self.importsettings:
            self._import_skinsettings()
        elif self.importextrathumb:
            self._AddArtToLibrary("extrathumb","Movie","extrathumbs",extrathumb_limit,True)
        elif self.importextrafanart:
            self._AddArtToLibrary("extrafanart","Movie","extrafanart",extrafanart_limit,True)
   #     elif self.importextrathumbtv:
  #          self._AddArtToLibrary("extrathumb","TVShow","extrathumbs")
        elif self.importextrafanarttv:
            self._AddArtToLibrary("extrafanart","TVShow","extrafanart",extrafanart_limit,True)
        elif self.importallartwork:
            self._AddArtToLibrary("extrathumb","Movie","extrathumbs",extrathumb_limit,True)
            self._AddArtToLibrary("extrafanart","Movie","extrafanart",extrafanart_limit,True)
            self._AddArtToLibrary("extrafanart","TVShow","extrafanart",extrafanart_limit,True)
        elif self.backend and xbmc.getCondVisibility("IsEmpty(Window(home).Property(extendedinfo_backend_running))"):
            xbmc.executebuiltin('SetProperty(extendedinfo_backend_running,True,home)')
            self.run_backend()
        # only set new properties if artistid is not smaller than 0, e.g. -1
        elif self.artistid and self.artistid > -1:
            self._set_details(self.artistid)
        # else clear old properties
        elif not len(sys.argv) >1:
            self._selection_dialog()
            
    def _selection_dialog(self):
        modeselect= []
        modeselect.append( __language__(32001) )
        modeselect.append( __language__(32002) )
        modeselect.append( __language__(32003) )
        modeselect.append( __language__(32014) )
        modeselect.append( __language__(32015) )
     #   modeselect.append( __language__(32014) + " (TV)" )
        modeselect.append( __language__(32015) + " (TV)" )
        modeselect.append( "Update All" )
        dialogSelection = xbmcgui.Dialog()
        selection        = dialogSelection.select( __language__(32004), modeselect ) 
        if selection == 0:
            self._export_skinsettings()
        elif selection == 1:
            self._import_skinsettings()
        elif selection == 2:
            xbmc.executebuiltin("Skin.ResetSettings")
        elif selection == 3:
            self._AddArtToLibrary("extrathumb","Movie", "extrathumbs",extrathumb_limit)
        elif selection == 4:
            self._AddArtToLibrary("extrafanart","Movie", "extrafanart",extrafanart_limit)
   #     elif selection == 5:
    #        self._AddArtToLibrary("extrathumb","TVShow", "extrathumbs")
        elif selection == 5:
            self._AddArtToLibrary("extrafanart","TVShow", "extrafanart",extrafanart_limit)
        elif selection == 6:
            self._AddArtToLibrary("extrathumb","Movie", "extrathumbs",extrathumb_limit)
            self._AddArtToLibrary("extrafanart","Movie", "extrafanart",extrafanart_limit)
            self._AddArtToLibrary("extrafanart","TVShow", "extrafanart",extrafanart_limit)

            
    def _init_vars(self):
        self.window = xbmcgui.Window(10000) # Home Window
        self.cleared = False
        self.musicvideos = []
        self.movies = []
        self.window.clearProperty('SongToMusicVideo.Path')

    def _parse_argv(self):
        try:
            params = dict( arg.split("=") for arg in sys.argv[1].split("&"))
        except:
            params = {}
        self.artistid = -1
        try: self.artistid = int(params.get("artistid", "-1"))
        except: pass
        self.backend = params.get("backend", False)
        self.type = params.get("type", False)
        self.info = params.get("info", False)
        self.exportsettings = params.get("exportsettings", False)
        self.importsettings = params.get("importsettings", False)
        self.importextrathumb = params.get("importextrathumb", False)
        self.importextrathumbtv = params.get("importextrathumbtv", False)
        self.importextrafanart = params.get("importextrafanart", False)
        self.importextrafanarttv = params.get("importextrafanarttv", False)
        self.importallartwork = params.get("importallartwork", False)
        for arg in sys.argv:
            if arg == 'script.extendedinfo':
                continue
            param = arg.lower()
            if param.startswith('info='):
                infos.append(param[5:])
            elif param.startswith('artistname='):
                ArtistName = arg[11:]
                # todo: look up local mbid first -->xbmcid for parameter
                from MusicBrainz import GetMusicBrainzIdFromNet
                Artist_mbid = GetMusicBrainzIdFromNet(ArtistName)
            elif param.startswith('albumname='):
                AlbumName = arg[10:]
            elif param.startswith('tracktitle='):
                TrackTitle = arg[11:]
            elif param.startswith('window='):
                Window = int(arg[7:])
            elif param.startswith('setuplocation'):
                settings = xbmcaddon.Addon(id='script.extendedinfo')
                country = settings.getSetting('country')
                city = settings.getSetting('city')
                log('stored country/city: %s/%s' % (country, city) )  
                kb = xbmc.Keyboard('', __language__(32013) + ":")
                kb.doModal()
                country = kb.getText()
                kb = xbmc.Keyboard('', __language__(32012) + ":")
                kb.doModal()
                city = kb.getText()
                log('country/city: %s/%s' % (country, city) )         
                settings.setSetting('location_method', 'country_city')
                settings.setSetting('country',country)
                settings.setSetting('city',city)
                log('done with settings')
            else:
                AdditionalParams.append(param)
        passDataToSkin('SimilarArtists', None)
        passDataToSkin('MusicEvents', None)
        
        
    def _create_musicvideo_list( self ):
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["artist", "file"], "sort": { "method": "artist" } }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if (json_response['result'] != None) and (json_response['result'].has_key('musicvideos')):
            # iterate through the results
            for item in json_response['result']['musicvideos']:
                artist = item['artist']
                title = item['label']
                path = item['file']
                self.musicvideos.append((artist,title,path))
        log('musicvideos: %s' % self.musicvideos)
        
    def _create_movie_list( self ):
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["year", "file", "art", "genre", "director","cast","studio","country","tag"], "sort": { "method": "label" } }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if (json_response['result'] != None) and (json_response['result'].has_key('movies')):
            # iterate through the results
            for item in json_response['result']['movies']:
                year = item['year']
                path = item['file']
                art = item['art']
                genre = item['genre']
                director = item['director']
                cast = item['cast']
                studio = item['studio']
                country = item['country']
                tag = item['tag']
                self.movies.append((year,path,art,genre,director,cast,studio,country,tag))               
                               
    def _AddArtToLibrary( self, type, media, folder, limit , silent = False):
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

    def _export_skinsettings( self ):
        import xbmcvfs
        from xml.dom.minidom import parse
        # Set path
        self.guisettings_path = xbmc.translatePath( 'special://profile/guisettings.xml' ).decode("utf-8")
        # Check to see if file exists
        if xbmcvfs.exists( self.guisettings_path ):
            log("guisettings.xml found")
            self.doc = parse( self.guisettings_path )
            skinsettings = self.doc.documentElement.getElementsByTagName( 'setting' )
            newlist = []
            for count, skinsetting in enumerate(skinsettings):
                if skinsetting.childNodes:
                    value = skinsetting.childNodes [ 0 ].nodeValue
                else:
                    value = ""
                if skinsetting.attributes[ 'name' ].nodeValue.startswith(xbmc.getSkinDir()):
                    newlist.append((skinsetting.attributes[ 'type' ].nodeValue,skinsetting.attributes[ 'name' ].nodeValue,value))
            if self._save_to_file(newlist,"backup"):
                xbmcgui.Dialog().ok(__language__(32005),__language__(32006))
        else:
            xbmcgui.Dialog().ok(__language__(32007),__language__(32008))
            log("guisettings.xml not found")
            
            
    def _save_to_file( self, content, suffix, path = "" ):
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
        except Exception:
            sys.exc_clear()
            return False
        
    def _import_skinsettings( self ):
        import xbmcvfs
        # Set path
        self.backup_path = get_browse_dialog(dlg_type=1)
        # Check to see if file exists
        if xbmcvfs.exists( self.backup_path ):
            log("backup found")
            with open(self.backup_path) as f: fc = simplejson.load(f)
            progressDialog = xbmcgui.DialogProgress(__language__(32010))
            progressDialog.create(__language__(32010))
            xbmc.sleep(200)
            for count, skinsetting in enumerate(fc):
                if progressDialog.iscanceled():
                    return
                if skinsetting[1].startswith(xbmc.getSkinDir()):
                    progressDialog.update( (count * 100) / len(fc)  , __language__(32011) + ' %s' % skinsetting[1])
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

    def _set_detail_properties( self, movie,count):
        self.window.setProperty('Detail.Movie.%i.Path' % (count), movie[1])
        self.window.setProperty('Detail.Movie.%i.Art(fanart)' % (count), movie[2].get('fanart',''))
        self.window.setProperty('Detail.Movie.%i.Art(poster)' % (count), movie[2].get('poster',''))      

    def _detail_selector( self, comparator):
        self.selecteditem = xbmc.getInfoLabel("ListItem.Label")
        if (self.selecteditem != self.previousitem):
            self.previousitem = self.selecteditem
            if xbmc.getCondVisibility("!Stringcompare(ListItem.Label,..)"):
                self._clear_properties()
                count = 1
                for movie in self.movies:
                    if self.selecteditem in str(movie[comparator]):
                        self._set_detail_properties(movie,count)
                        count +=1
                    if count > 19:
                        break
            else:
                self._clear_properties()
        xbmc.sleep(100)        
                        
    def run_backend(self):
        self._stop = False
        self.previousitem = ""
        self.previousartist = ""
        self.previoussong = ""
        self._create_musicvideo_list()
        self._create_movie_list()
        while (not self._stop) and (not xbmc.abortRequested):
            if xbmc.getCondVisibility("Container.Content(movies) | Container.Content(sets)"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if xbmc.getCondVisibility("!IsEmpty(ListItem.DBID) + SubString(ListItem.Path,videodb://1/7/,left)"):
                        self._set_details(xbmc.getInfoLabel("ListItem.DBID"))
                        xbmc.sleep(100)
                    else:
                        self._clear_properties()
            elif xbmc.getCondVisibility("Container.Content(artists) | Container.Content(albums)"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if xbmc.getCondVisibility("!IsEmpty(ListItem.DBID)"):
                        self._set_details(xbmc.getInfoLabel("ListItem.DBID"))
                        xbmc.sleep(100)
                    else:
                        self._clear_properties()
            elif xbmc.getCondVisibility("Container.Content(years)"):
                self._detail_selector(0)
            elif xbmc.getCondVisibility("Container.Content(genres)"):
                self._detail_selector(3)              
            elif xbmc.getCondVisibility("Container.Content(directors)"):
                self._detail_selector(4)
            elif xbmc.getCondVisibility("Container.Content(actors)"):
                self._detail_selector(5)
            elif xbmc.getCondVisibility("Container.Content(studios)"):
                self._detail_selector(6)
            elif xbmc.getCondVisibility("Container.Content(countries)"):
                self._detail_selector(7)
            elif xbmc.getCondVisibility("Container.Content(tags)"):
                self._detail_selector(8)                       
            elif xbmc.getCondVisibility('Container.Content(songs)'):
                # get artistname and songtitle of the selected item
                artist = xbmc.getInfoLabel('ListItem.Artist')
                song = xbmc.getInfoLabel('ListItem.Title')
                # check if we've focussed a new song
                if (artist != self.previousartist) and (song != self.previoussong):
                    # clear the window property
                    self.window.clearProperty('SongToMusicVideo.Path')
                    # iterate through our musicvideos
                    for musicvideo in self.musicvideos:
                        if artist == musicvideo[0] and song == musicvideo[1]:
                            # match found, set the window property
                            self.window.setProperty('SongToMusicVideo.Path', musicvideo[2])
                            xbmc.sleep(100)
                            # stop iterating
                            break
            else:
                self._clear_properties()
                xbmc.sleep(1000)
            if xbmc.getCondVisibility("!Window.IsActive(musiclibrary) + !Window.IsActive(videos)"):
                xbmc.sleep(500)               
            xbmc.sleep(100)
            if xbmc.getCondVisibility("IsEmpty(Window(home).Property(extendedinfo_backend_running))"):
                self._clear_properties()
                self._stop = True
                
    def _set_details( self, dbid ):
        if dbid:
            try:
                b = ""
                if xbmc.getCondVisibility('Container.Content(artists)') or self.type == "artist":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "year", "albumlabel", "playcount", "thumbnail"], "sort": { "method": "label" }, "filter": {"artistid": %s} }, "id": 1}' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_response = simplejson.loads(json_query)
                    self._clear_properties()
                    if json_response['result'].has_key('albums'):
                        self._set_artist_properties(json_response)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('Container.Content(albums)') or self.type == "album":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "track", "duration", "file", "lastplayed", "disc"], "sort": { "method": "label" }, "filter": {"albumid": %s} }, "id": 1}' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if json_query.has_key('result') and json_query['result'].has_key('songs'):
                        self._set_album_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('[Container.Content(movies) + ListItem.IsFolder] | Container.Content(sets)') or self.type == "set":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "file", "year", "director", "writer","genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country"], "sort": { "order": "ascending",  "method": "year" }} },"id": 1 }' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if json_query.has_key('result') and json_query['result'].has_key('setdetails'):
                        self._set_movie_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('Container.Content(songs)') or self.type == "songs":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["artist", "file"], "sort": { "method": "artist" } }, "id": 1}')
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if json_query.has_key('result') and json_query['result'].has_key('musicvideos'):
                        self._set_movie_properties(json_query)
                    b = datetime.datetime.now() - a
                if b:
                    log('Total time needed to request: %s' % b)
            except Exception, e:
                log(e)
            
    def _set_artist_properties( self, audio ):
        count = 1
        latestyear = 0
        firstyear = 0
        playcount = 0
        for item in audio['result']['albums']:
            self.window.setProperty('Artist.Album.%d.Title' % count, item['title'])
            self.window.setProperty('Artist.Album.%d.Year' % count, str(item['year']))
            self.window.setProperty('Artist.Album.%d.Thumb' % count, item['thumbnail'])
            self.window.setProperty('Artist.Album.%d.DBID' % count, str(item.get('albumid')))
            self.window.setProperty('Artist.Album.%d.Label' % count, item['albumlabel'])
            if item['playcount']:
                playcount = playcount + item['playcount']
            if item['year']:
                if item['year'] > latestyear:
                    latestyear = item['year']
                if firstyear == 0 or item['year'] < firstyear:
                    firstyear = item['year']
            count += 1
        self.window.setProperty('Artist.Albums.Newest', str(latestyear))
        self.window.setProperty('Artist.Albums.Oldest', str(firstyear))
        self.window.setProperty('Artist.Albums.Count', str(audio['result']['limits']['total']))
        self.window.setProperty('Artist.Albums.Playcount', str(playcount))
        self.cleared = False
  
    def _set_album_properties( self, json_query ):
        count = 1
        duration = 0
        discnumber = 0
        tracklist=""
        for item in json_query['result']['songs']:
            self.window.setProperty('Album.Song.%d.Title' % count, item['title'])
            tracklist += "[B]" + str(item['track']) + "[/B]: " + item['title'] + "[CR]"
            array = item['file'].split('.')
            self.window.setProperty('Album.Song.%d.FileExtension' % count, str(array[-1]))
            if item['disc'] > discnumber:
                discnumber = item['disc']
            duration += item['duration']
            count += 1
        self.window.setProperty('Album.Songs.Discs', str(discnumber))
        self.window.setProperty('Album.Songs.Duration', str(duration))
        self.window.setProperty('Album.Songs.Tracklist', tracklist)
        self.window.setProperty('Album.Songs.Count', str(json_query['result']['limits']['total']))
        self.cleared = False
        
    def _set_movie_properties( self, json_query ):
        count = 1
        runtime = 0
        writer = []
        director = []
        genre = []
        country = []
        studio = []
        years = []
        plot = ""
        title_list = ""
        title_list += "[B]" + str(json_query['result']['setdetails']['limits']['total']) + " " + xbmc.getLocalizedString(20342) + "[/B][CR][I]"
        for item in json_query['result']['setdetails']['movies']:
            art = item['art']
            self.window.setProperty('Set.Movie.%d.DBID' % count, str(item.get('movieid')))
            self.window.setProperty('Set.Movie.%d.Title' % count, item['label'])
            self.window.setProperty('Set.Movie.%d.Plot' % count, item['plot'])
            self.window.setProperty('Set.Movie.%d.PlotOutline' % count, item['plotoutline'])
            self.window.setProperty('Set.Movie.%d.Path' % count, media_path(item['file']))
            self.window.setProperty('Set.Movie.%d.Year' % count, str(item['year']))
            self.window.setProperty('Set.Movie.%d.Duration' % count, str(item['runtime']/60))
            self.window.setProperty('Set.Movie.%d.Art(clearlogo)' % count, art.get('clearlogo',''))
            self.window.setProperty('Set.Movie.%d.Art(discart)' % count, art.get('discart',''))
            self.window.setProperty('Set.Movie.%d.Art(fanart)' % count, art.get('fanart',''))
            self.window.setProperty('Detail.Movie.%d.Art(fanart)' % count, art.get('fanart',''))
            self.window.setProperty('Set.Movie.%d.Art(poster)' % count, art.get('poster',''))
            self.window.setProperty('Detail.Movie.%d.Art(poster)' % count, art.get('poster',''))
            title_list += item['label'] + " (" + str(item['year']) + ")[CR]"            
            if item['plotoutline']:
                plot += "[B]" + item['label'] + " (" + str(item['year']) + ")[/B][CR]" + item['plotoutline'] + "[CR][CR]"
            else:
                plot += "[B]" + item['label'] + " (" + str(item['year']) + ")[/B][CR]" + item['plot'] + "[CR][CR]"
            runtime += item['runtime']
            count += 1
            if item.get( "writer" ):   writer += [ w for w in item[ "writer" ] if w and w not in writer ]
            if item.get( "director" ): director += [ d for d in item[ "director" ] if d and d not in director ]
            if item.get( "genre" ): genre += [ g for g in item[ "genre" ] if g and g not in genre ]
            if item.get( "country" ): country += [ c for c in item[ "country" ] if c and c not in country ]
            if item.get( "studio" ): studio += [ s for s in item[ "studio" ] if s and s not in studio ]
        #    years += [ str(item['year']) ]
            years.append(str(item['year']))
        self.window.setProperty('Set.Movies.Plot', plot)
        if json_query['result']['setdetails']['limits']['total'] > 1:
            self.window.setProperty('Set.Movies.ExtendedPlot', title_list + "[/I][CR]" + plot)
        else:
            self.window.setProperty('Set.Movies.ExtendedPlot', plot)        
        self.window.setProperty('Set.Movies.Runtime', str(runtime/60))
        self.window.setProperty('Set.Movies.Writer', " / ".join( writer ))
        self.window.setProperty('Set.Movies.Director', " / ".join( director ))
        self.window.setProperty('Set.Movies.Genre', " / ".join( genre ))
        self.window.setProperty('Set.Movies.Country', " / ".join( country ))
        self.window.setProperty('Set.Movies.Studio', " / ".join( studio ))
        self.window.setProperty('Set.Movies.Years', " / ".join( years ))
        self.window.setProperty('Set.Movies.Count', str(json_query['result']['limits']['total']))
        self.cleared = False
  
    def _clear_properties( self ):
        #todo
        self.cleared = False
        if not self.cleared:
            for i in range(1,50):
                self.window.clearProperty('Artist.Album.%d.Title' % i)
                self.window.clearProperty('Artist.Album.%d.Plot' % i)
                self.window.clearProperty('Artist.Album.%d.PlotOutline' % i)
                self.window.clearProperty('Artist.Album.%d.Year' % i)
                self.window.clearProperty('Artist.Album.%d.Duration' % i)
                self.window.clearProperty('Artist.Album.%d.Thumb' % i)
                self.window.clearProperty('Artist.Album.%d.ID' % i)
                self.window.clearProperty('Album.Song.%d.Title' % i)
                self.window.clearProperty('Album.Song.%d.FileExtension' % i)   
                self.window.clearProperty('Set.Movie.%d.Art(clearlogo)' % i)
                self.window.clearProperty('Set.Movie.%d.Art(fanart)' % i)
                self.window.clearProperty('Set.Movie.%d.Art(poster)' % i)
                self.window.clearProperty('Set.Movie.%d.Art(discart)' % i)
                self.window.clearProperty('Detail.Movie.%d.Art(poster)' % i)
                self.window.clearProperty('Detail.Movie.%d.Art(fanart)' % i)
                self.window.clearProperty('Detail.Movie.%d.Art(Path)' % i)
            self.window.clearProperty('Album.Songs.TrackList')   
            self.window.clearProperty('Album.Songs.Discs')   
            self.window.clearProperty('Artist.Albums.Newest')   
            self.window.clearProperty('Artist.Albums.Oldest')   
            self.window.clearProperty('Artist.Albums.Count')   
            self.window.clearProperty('Artist.Albums.Playcount')   
            self.window.clearProperty('Album.Songs.Discs')   
            self.window.clearProperty('Album.Songs.Duration')   
            self.window.clearProperty('Album.Songs.Count')   
            self.window.clearProperty('Set.Movies.Plot')   
            self.window.clearProperty('Set.Movies.ExtendedPlot')   
            self.window.clearProperty('Set.Movies.Runtime')   
            self.window.clearProperty('Set.Movies.Writer')   
            self.window.clearProperty('Set.Movies.Director')   
            self.window.clearProperty('Set.Movies.Genre')   
            self.window.clearProperty('Set.Movies.Years')   
            self.window.clearProperty('Set.Movies.Count')   
            self.cleared = True

if ( __name__ == "__main__" ):
    Main()
log('finished')
