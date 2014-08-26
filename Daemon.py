import sys
import os, datetime
import xbmc, xbmcgui, xbmcaddon
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__     = __addon__.getLocalizedString

Window = 10000

class Daemon:
    def __init__( self ):
        log("version %s started" % __addonversion__ )
        xbmc.executebuiltin('SetProperty(extendedinfo_backend_running,True,home)')
        self._init_vars()
        self.run_backend()

    def _init_vars(self):
        self.window = xbmcgui.Window(10000) # Home Window
        self.musicvideos = []
        self.movies = []
        self.id = None
        self.dbid = None
        self.type = False
        self.tag = ""
        self.silent = True
        self.prop_prefix = ""
        self.Artist_mbid = None
        self.window.clearProperty('SongToMusicVideo.Path')            
            
    def run_backend(self):
        self._stop = False
        self.previousitem = ""
        self.previousartist = ""
        self.previoussong = ""
        log("starting backend")
        self.musicvideos = create_musicvideo_list()
        self.movies = create_movie_list()
        while (not self._stop) and (not xbmc.abortRequested):
            log("Daemon active")
            if xbmc.getCondVisibility("Container.Content(movies) | Container.Content(sets) | Container.Content(artists) | Container.Content(albums)"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if xbmc.getCondVisibility("!IsEmpty(ListItem.DBID) + [SubString(ListItem.Path,videodb://movies/sets/,left)| Container.Content(artists) | Container.Content(albums)]"):
                        self._set_details(xbmc.getInfoLabel("ListItem.DBID"))
                        log("setting movieset labels")
                    else:
                        clear_properties()
            elif xbmc.getCondVisibility("Container.Content(years)"):
                self._detail_selector("year")            
            elif xbmc.getCondVisibility("Container.Content(genres)"):
                self._detail_selector("genre")              
            elif xbmc.getCondVisibility("Container.Content(directors)"):
                self._detail_selector("director")
            elif xbmc.getCondVisibility("Container.Content(actors)"):
                self._detail_selector("cast")
            elif xbmc.getCondVisibility("Container.Content(studios)"):
                self._detail_selector("studio")
            elif xbmc.getCondVisibility("Container.Content(countries)"):
                self._detail_selector("country")
            elif xbmc.getCondVisibility("Container.Content(tags)"):
                self._detail_selector("tag")                       
            elif xbmc.getCondVisibility('Container.Content(songs)') and self.musicvideos:
                # get artistname and songtitle of the selected item
                self.selecteditem = xbmc.getInfoLabel('ListItem.DBID')
                # check if we've focussed a new song
                if self.selecteditem != self.previousitem:
                    self.previousitem = self.selecteditem
                    # clear the window property
                    self.window.clearProperty('SongToMusicVideo.Path')
                    # iterate through our musicvideos
                    for musicvideo in self.musicvideos:
                        if self.selecteditem == musicvideo[0]:#needs fixing
                            # match found, set the window property
                            self.window.setProperty('SongToMusicVideo.Path', musicvideo[2])
                            xbmc.sleep(100)
                            # stop iterating
                            break
            elif xbmc.getCondVisibility("Window.IsActive(visualisation)"):
                self.selecteditem = xbmc.getInfoLabel('MusicPlayer.Artist')
                if (self.selecteditem != self.previousitem) and self.selecteditem:
                    self.previousitem = self.selecteditem
                    from MusicBrainz import GetMusicBrainzIdFromNet
                    log("Daemon updating SimilarArtists")
                    Artist_mbid = GetMusicBrainzIdFromNet(self.selecteditem)
                    passDataToSkin('SimilarArtistsInLibrary', None, self.prop_prefix)
                    passDataToSkin('SimilarArtists', GetSimilarArtistsInLibrary(Artist_mbid), self.prop_prefix)
            elif xbmc.getCondVisibility('Window.IsActive(screensaver)'):
                xbmc.sleep(1000)
            else:
                self.previousitem = ""
                self.selecteditem = ""    
                clear_properties()
                xbmc.sleep(500)     
            if xbmc.getCondVisibility("IsEmpty(Window(home).Property(extendedinfo_backend_running))"):
                clear_properties()
                self._stop = True
            xbmc.sleep(100)     

    def _set_details( self, dbid ):
        if dbid:
            try:
                b = ""
                if xbmc.getCondVisibility('Container.Content(artists)') or self.type == "artist":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "year", "albumlabel", "playcount", "thumbnail"], "sort": { "method": "label" }, "filter": {"artistid": %s} }, "id": 1}' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    clear_properties()
                    if json_query['result'].has_key('albums'):
                        set_artist_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('Container.Content(albums)') or self.type == "album":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "track", "duration", "file", "lastplayed", "disc"], "sort": { "method": "label" }, "filter": {"albumid": %s} }, "id": 1}' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    clear_properties()
                    if "result" in json_query and json_query['result'].has_key('songs'):
                        set_album_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('[Container.Content(movies) + ListItem.IsFolder] | Container.Content(sets)') or self.type == "set":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "file", "year", "director", "writer","genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country"], "sort": { "order": "ascending",  "method": "year" }} },"id": 1 }' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    clear_properties()
                    if "result" in json_query and json_query['result'].has_key('setdetails'):
                        set_movie_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('Container.Content(songs)') or self.type == "songs":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["artist", "file"], "sort": { "method": "artist" } }, "id": 1}')
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    clear_properties()
                    if "result" in json_query and json_query['result'].has_key('musicvideos'):
                        set_movie_properties(json_query)
                    b = datetime.datetime.now() - a
                if b:
                    log('Total time needed to request: %s' % b)
            except Exception, e:
                log(e)
                
    def _detail_selector( self, comparator):
        self.selecteditem = xbmc.getInfoLabel("ListItem.Label")
        if (self.selecteditem != self.previousitem):
            if xbmc.getCondVisibility("!Stringcompare(ListItem.Label,..)"):
                self.previousitem = self.selecteditem
                clear_properties()
                count = 1
                for movie in self.movies["result"]["movies"]:
                    log(comparator)
                    if self.selecteditem in str(movie[comparator]):
                        log(movie)
                        self._set_detail_properties(movie,count)
                        count +=1
                    if count > 19:
                        break
            else:
                clear_properties()            
            