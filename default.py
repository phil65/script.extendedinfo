import sys
import xbmc, xbmcgui, xbmcaddon
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')

def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

class Main:
    def __init__( self ):
        log("version %s started" % __addonversion__ )
        self._init_vars()
        self._parse_argv()
        # run in backend if parameter was set
        if xbmc.getCondVisibility("IsEmpty(Window(home).Property(artistalbums_backend_running))"):
            if self.backend:
                xbmc.executebuiltin('SetProperty(artistalbums_backend_running,true,home)')
                self.run_backend()
            # only set new properties if artistid is not smaller than 0, e.g. -1
            elif self.artistid and self.artistid > -1:
                self._set_details(self.artistid)
            # else clear old properties
            else:
                self._clear_properties()
            
    def _init_vars(self):
        self.window = xbmcgui.Window(10502) # Music Library Window
        self.cleared = False

    def _parse_argv(self):
        try:
            params = dict( arg.split("=") for arg in sys.argv[1].split("&"))
        except:
            params = {}
        log("params: %s" % params)
        self.artistid = -1
        try: self.artistid = int(params.get("artistid", "-1"))
        except: pass
        self.backend = params.get("backend", False)
        self.type = str(params.get("type", False))

    def run_backend(self):
        self._stop = False
        self.previousitem = ""
        while not self._stop:
            if xbmc.getCondVisibility("Container.Content(artists)") or xbmc.getCondVisibility("Container.Content(albums)")or xbmc.getCondVisibility("Container.Content(movies)"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if xbmc.getInfoLabel("ListItem.DBID") > -1:
                        self._set_details(xbmc.getInfoLabel("ListItem.DBID"))
                        xbmc.sleep(100)
                    else:
                        self._clear_properties()
            else:
                self._clear_properties()
                xbmc.sleep(1000)
            xbmc.sleep(100)
       #     if not xbmc.getCondVisibility("Window.IsVisible(musiclibrary)"):
        #        self._clear_properties()
         #       xbmc.executebuiltin('ClearProperty(artistalbums_backend_running,home)')
          #      self._stop = True

    def _set_details( self, dbid ):
        try:
            if xbmc.getCondVisibility('Container.Content(artists)') or self.type == "artist":
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "year", "albumlabel", "playcount", "thumbnail"], "sort": { "method": "label" }, "filter": {"artistid": %s} }, "id": 1}' % dbid)
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                log(json_query)
                json_response = simplejson.loads(json_query)
                self._clear_properties()
                if json_response['result'].has_key('albums'):
                    self._set_artist_properties(json_response)
            elif xbmc.getCondVisibility('Container.Content(albums)') or self.type == "album":
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": ["title","track","duration", "file", "lastplayed", "disc"], "sort": { "method": "label" }, "filter": {"albumid": %s} }, "id": 1}' % dbid)
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                log(json_query)
                json_query = simplejson.loads(json_query)
                self._clear_properties()
                if json_query.has_key('result') and json_query['result'].has_key('songs'):
                    self._set_album_properties(json_query)
            elif (xbmc.getCondVisibility('Container.Content(movies)') and xbmc.getCondVisibility('ListItem.IsFolder')) or self.type == "set":
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "director", "writer","genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country", "year" ], "sort": { "order": "ascending",  "method": "year" }} },"id": 1 }' % dbid)
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                log(json_query)
                json_query = simplejson.loads(json_query)
                self._clear_properties()
                if json_query.has_key('result') and json_query['result'].has_key('setdetails'):
                    self._set_movie_properties(json_query)
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
            self.window.setProperty('Artist.Album.%d.ID' % count, str(item.get('albumid')))
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
            log(tracklist)
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
        plot = ""
        for item in json_query['result']['setdetails']['movies']:
            art = item['art']
          #  self.window.setProperty('Set.Movie.%d.Title' % count, item['title'])
            self.window.setProperty('Set.Movie.%d.Art(clearlogo)' % count, art.get('clearlogo',''))
            self.window.setProperty('Set.Movie.%d.Art(fanart)' % count, art.get('fanart',''))
            self.window.setProperty('Set.Movie.%d.Art(poster)' % count, art.get('poster',''))
       #     self.window.setProperty('Set.Movie.%d.PlotOutline' % count, item['plotoutline'])
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
        self.window.setProperty('Set.Movies.Plot', plot)
        self.window.setProperty('Set.Movies.Runtime', str(runtime/60))
        self.window.setProperty('Set.Movies.Writer', " / ".join( writer ))
        self.window.setProperty('Set.Movies.Director', " / ".join( director ))
        self.window.setProperty('Set.Movies.Genre', " / ".join( genre ))
        self.window.setProperty('Set.Movies.Country', " / ".join( country ))
        self.window.setProperty('Set.Movies.Studio', " / ".join( studio ))
        self.window.setProperty('Set.Movies.Count', str(json_query['result']['limits']['total']))
        self.cleared = False
  
    def _clear_properties( self ):
        #todo
        self.cleared = False
        if not self.cleared:
            for i in range(1,50):
                self.window.clearProperty('Artist.Album.%d.Title' % i)
                self.window.clearProperty('Artist.Album.%d.Year' % i)
                self.window.clearProperty('Artist.Album.%d.Thumb' % i)
                self.window.clearProperty('Artist.Album.%d.ID' % i)
                self.window.clearProperty('Album.Song.%d.Title' % i)
                self.window.clearProperty('Set.Movie.%d.Art(clearlogo)' % i)
                self.window.clearProperty('Set.Movie.%d.Art(fanart)' % i)
                self.window.clearProperty('Set.Movie.%d.Art(poster)' % i)
            self.window.clearProperty('Artist.Albums.Newest')   
            self.window.clearProperty('Artist.Albums.Oldest')   
            self.window.clearProperty('Artist.Albums.Count')   
            self.window.clearProperty('Artist.Albums.Playcount')   
            self.window.clearProperty('Album.Songs.Discs')   
            self.window.clearProperty('Album.Songs.Duration')   
            self.window.clearProperty('Album.Songs.Count')   
            self.window.clearProperty('Set.Movies.Plot')   
            self.window.clearProperty('Set.Movies.Runtime')   
            self.window.clearProperty('Set.Movies.Writer')   
            self.window.clearProperty('Set.Movies.Director')   
            self.window.clearProperty('Set.Movies.Genre')   
            self.window.clearProperty('Set.Movies.Count')   
            self.cleared = True

if ( __name__ == "__main__" ):
    Main()
log('finished')
