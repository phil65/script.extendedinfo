import sys
import os, time, datetime
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__     = __addon__.getLocalizedString


TrackTitle = None
AdditionalParams = []
Window = 10000
extrathumb_limit = 4
extrafanart_limit = 10
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % __addonid__ ).decode("utf-8") )
Skin_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmc.getSkinDir() ).decode("utf-8") )

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
                        _set_artist_properties(json_query)
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
            
class Main:
    def __init__( self ):
        log("version %s started" % __addonversion__ )
        xbmc.executebuiltin('SetProperty(extendedinfo_running,True,home)')
        self._init_vars()
        self._parse_argv()
        # run in backend if parameter was set
        if self.infos:
            self._StartInfoActions()
        elif self.exportsettings:
            export_skinsettings()        
        elif self.importsettings:
            import_skinsettings()
        elif self.importextrathumb:
            AddArtToLibrary("extrathumb","Movie","extrathumbs",extrathumb_limit,True)
        elif self.importextrafanart:
            AddArtToLibrary("extrafanart","Movie","extrafanart",extrafanart_limit,True)
   #     elif self.importextrathumbtv:
  #          AddArtToLibrary("extrathumb","TVShow","extrathumbs")
        elif self.importextrafanarttv:
            AddArtToLibrary("extrafanart","TVShow","extrafanart",extrafanart_limit,True)
        elif self.importallartwork:
            AddArtToLibrary("extrathumb","Movie","extrathumbs",extrathumb_limit,True)
            AddArtToLibrary("extrafanart","Movie","extrafanart",extrafanart_limit,True)
            AddArtToLibrary("extrafanart","TVShow","extrafanart",extrafanart_limit,True)
        elif not len(sys.argv) >1:
            self._selection_dialog()
        xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')


    def _StartInfoActions(self):
        if not self.silent:
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        for info in self.infos:
            if info == 'json':
                from MiscScraper import GetYoutubeVideos
                videos = GetYoutubeVideos(self.feed,self.prop_prefix)
                passDataToSkin('RSS', videos, self.prop_prefix)
            elif info == 'similarlocal' and self.dbid:
                passDataToSkin('SimilarLocalMovies', None , self.prop_prefix)
                passDataToSkin('SimilarLocalMovies', GetSimilarFromOwnLibrary(self.dbid) , self.prop_prefix)                       
            elif info == 'xkcd':
                log("startin GetXKCDInfo")
                from MiscScraper import GetXKCDInfo
                passDataToSkin('XKCD', GetXKCDInfo(), self.prop_prefix)
            elif info == 'flickr':
                from MiscScraper import GetFlickrImages
                log("startin flickr")
                passDataToSkin('Flickr', GetFlickrImages(), self.prop_prefix)
            elif info == 'discography':
                passDataToSkin('Discography', None, self.prop_prefix)
                log("startin gettopalbums")
                from OnlineMusicInfo import GetArtistTopAlbums
                passDataToSkin('Discography', GetArtistTopAlbums(self.Artist_mbid), self.prop_prefix)
            elif info == 'artistdetails':
                passDataToSkin('Discography', None, self.prop_prefix)
                passDataToSkin('MusicVideos', None, self.prop_prefix)
                log("startin ArtistDetails")
                from TheAudioDB import GetDiscography, GetArtistDetails, GetMostLovedTracks, GetMusicVideos
                ArtistDetails = GetArtistDetails(self.ArtistName)
                if "audiodbid" in ArtistDetails:
                    MusicVideos = GetMusicVideos(ArtistDetails["audiodbid"])
                    passDataToSkin('MusicVideos', MusicVideos, self.prop_prefix)
            #    GetAudioDBData("search.php?s=Blur")
                GetMostLovedTracks(self.ArtistName)
            #    from TheAudioDB import GetArtistTopAlbums
                passDataToSkin('Discography', GetDiscography(self.ArtistName), self.prop_prefix)
                passHomeDataToSkin(ArtistDetails)
            elif info == 'albuminfo':
                passHomeDataToSkin(None)
                log("startin ArtistDetails")
                from TheAudioDB import GetAlbumDetails, GetTrackDetails
                if self.id:
                    AlbumDetails = GetAlbumDetails(self.id)
                    Trackinfo = GetTrackDetails(self.id)
                    prettyprint(AlbumDetails)
                    passHomeDataToSkin(AlbumDetails)
                    passDataToSkin('Trackinfo', Trackinfo, self.prop_prefix)      
            elif info == 'shouts':
                log("startin shouts")
                passDataToSkin('Shout', None, self.prop_prefix)
                from OnlineMusicInfo import GetShouts
                if self.ArtistName and self.AlbumName:
                    passDataToSkin('Shout', GetShouts(self.ArtistName,self.AlbumName), self.prop_prefix,True)
            elif info == 'studio':
                passDataToSkin('StudioInfo', None, self.prop_prefix)
                if self.studio:
                    log("startin companyinfo")
                    from TheMovieDB import SearchforCompany, GetCompanyInfo
                    if self.studio:
                        CompanyId = SearchforCompany(self.studio)
                        passDataToSkin('StudioInfo', GetCompanyInfo(CompanyId), self.prop_prefix)
            elif info == 'set':
                passDataToSkin('MovieSetItems', None, self.prop_prefix)
                if self.dbid and not "show" in str(self.type):
                    from TheMovieDB import SearchForSet
                    name = GetMovieSetName(self.dbid)
                    if name:
                        log(name)
                        self.setid  = SearchForSet(name)   
                if self.setid:
                    log("startin SetInfo")
                    from TheMovieDB import GetSetMovies
                    SetData = GetSetMovies(self.setid)
                    if SetData:
                        passDataToSkin('MovieSetItems', SetData, self.prop_prefix)                
            elif info == 'topartists':
                passDataToSkin('TopArtists', None, self.prop_prefix)
                log("startin gettopartists")
                from OnlineMusicInfo import GetTopArtists
                passDataToSkin('TopArtists', GetTopArtists(), self.prop_prefix)
            elif info == 'cyanide':
                log("startin GetCandHInfo")
                from MiscScraper import GetCandHInfo
                passDataToSkin('CyanideHappiness', GetCandHInfo(), self.prop_prefix)

            ### RottenTomatoesMovies #################################################################################
            elif info == 'intheaters':
                log("start gettin intheaters info")
                from MiscScraper import GetRottenTomatoesMoviesInTheaters
                passDataToSkin('InTheatersMovies', GetRottenTomatoesMoviesInTheaters("in_theaters"), self.prop_prefix)
            elif info == 'boxoffice':
                log("start gettin boxoffice info")
                from MiscScraper import GetRottenTomatoesMoviesBoxOffice
                passDataToSkin('BoxOffice', GetRottenTomatoesMoviesBoxOffice("box_office"), self.prop_prefix)
            elif info == 'opening':
                log("start gettin opening info")
                from MiscScraper import GetRottenTomatoesMoviesOpening
                passDataToSkin('Opening', GetRottenTomatoesMoviesOpening("opening"), self.prop_prefix)
            elif info == 'comingsoon':
                log("start gettin comingsoon info")
                from MiscScraper import GetRottenTomatoesMoviesComingSoon
                passDataToSkin('ComingSoonMovies', GetRottenTomatoesMoviesComingSoon("upcoming"), self.prop_prefix)
            elif info == 'toprentals':
                log("start gettin toprentals info")
                from MiscScraper import GetRottenTomatoesMovies
                passDataToSkin('TopRentals', GetRottenTomatoesMovies("top_rentals"), self.prop_prefix)
                                
            ### The MovieDB ##########################################################################################
            elif info == 'incinemas':
                log("start gettin incinemasmovies info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('InCinemasMovies', GetMovieDBMovies("now_playing"), self.prop_prefix)
            elif info == 'upcoming':
                log("start gettin upcoming info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('UpcomingMovies', GetMovieDBMovies("upcoming"), self.prop_prefix)
            elif info == 'topratedmovies':
                log("start gettin topratedmovies info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('TopRatedMovies', GetMovieDBMovies("top_rated"), self.prop_prefix)
            elif info == 'popularmovies':
                log("start gettin popularmovies info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('PopularMovies', GetMovieDBMovies("popular"), self.prop_prefix)

            elif info == 'airingtodaytvshows':
                log("start gettin airingtodaytvshows info")
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('AiringTodayTVShows', GetMovieDBTVShows("airing_today"), self.prop_prefix)
            elif info == 'onairtvshows':
                log("start gettin onairtvshows info")
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('OnAirTVShows', GetMovieDBTVShows("on_the_air"), self.prop_prefix)
            elif info == 'topratedtvshows':
                log("start gettin topratedtvshows info")
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('TopRatedTVShows', GetMovieDBTVShows("top_rated"), self.prop_prefix)
            elif info == 'populartvshows':
                log("start gettin populartvshows info")
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('PopularTVShows', GetMovieDBTVShows("popular"), self.prop_prefix)                
 
            elif info == 'similarmovies':
                log("startin MovieDBGetSimilarMovies")
                passDataToSkin('SimilarMovies', None, self.prop_prefix)
                from TheMovieDB import GetSimilarMovies
                # MovieId = GetImdbID(self.id)
                if self.id:
                    MovieId = self.id
                elif self.dbid:
                    MovieId = GetImdbID("movie",self.dbid)
                    log("IMDBId from local DB:" + str(MovieId))
                else:
                    MovieId = ""
                if MovieId:
                    passDataToSkin('SimilarMovies', GetSimilarMovies(MovieId), self.prop_prefix)
            elif info == 'movielists':
                passDataToSkin('MovieLists', None, self.prop_prefix)
                if self.dbid:
                    log("startin movielists")
                    from TheMovieDB import GetMovieLists
                    id = GetImdbID("movie",self.dbid)
                    log("MovieDB Id:" + str(id))
                    if id:
                        passDataToSkin('MovieLists', GetMovieLists(id), self.prop_prefix)
            elif info == 'keywords':
                passDataToSkin('Keywords', None, self.prop_prefix)
                if self.dbid:
                    log("startin Keywords")
                    from TheMovieDB import GetMovieKeywords
                    id = GetImdbID("movie",self.dbid)
                    log("MovieDB Id:" + str(id))
                    if id:
                        passDataToSkin('Keywords', GetMovieKeywords(id), self.prop_prefix)                        
            elif info == 'extendedinfo':
                log("startin GetExtendedMovieInfo")
                if self.id:
                    MovieId = self.id
                elif self.dbid:
                    MovieId = GetImdbID("movie",self.dbid)
                    log("IMDBId from local DB:" + str(MovieId))
                else:
                    MovieId = ""
                if MovieId:
                    from TheMovieDB import GetExtendedMovieInfo
                    passHomeDataToSkin(GetExtendedMovieInfo(MovieId))
            elif info == 'extendedtvinfo':
                if self.id:
                    log("startin GetTVShowInfo")
                    from MiscScraper import GetTVShowInfo
                    passHomeDataToSkin(GetTVShowInfo(self.id)[0])
            elif info == 'directormovies':
                passDataToSkin('DirectorMovies', None, self.prop_prefix)
                if self.director:
                    log("startin GetDirectorMovies")
                    from TheMovieDB import GetDirectorMovies, GetPersonID
                    id = GetPersonID(self.director)
                    if id:
                        passDataToSkin('DirectorMovies', GetDirectorMovies(id), self.prop_prefix)
            elif info == 'writermovies':
                passDataToSkin('WriterMovies', None, self.prop_prefix)
                if self.writer and not self.writer.split(" / ")[0] == self.director.split(" / ")[0]:
                    log("startin GetWriterMovies")
                    from TheMovieDB import GetDirectorMovies, GetPersonID
                    id = GetPersonID(self.writer)
                    if id:
                        passDataToSkin('WriterMovies', GetDirectorMovies(id), self.prop_prefix)
            elif info == 'similar':
                passDataToSkin('SimilarMovies', None, self.prop_prefix)
                log("startin GetSimilarTrakt")
                log(self.dbid)
                log(self.id)
                log(self.type)
                from MiscScraper import GetSimilarTrakt
                if self.type and (self.id or self.dbid):
                    if self.dbid:
                        id = GetImdbID(self.type,self.dbid)
                        log("SimilarTrakt: found dbid " + str(id))
                    else:
                        id = self.id
                    passDataToSkin('SimilarMovies', GetSimilarTrakt(self.type,id), self.prop_prefix)                    
            elif info == 'airingshows':
                log("startin GetTraktCalendarShows")
                from MiscScraper import GetTraktCalendarShows
                passDataToSkin('AiringShows', GetTraktCalendarShows("shows"), self.prop_prefix)
            elif info == 'premiereshows':
                log("startin GetTraktCalendarShows")
                from MiscScraper import GetTraktCalendarShows
                passDataToSkin('PremiereShows', GetTraktCalendarShows("premieres"), self.prop_prefix)
            elif info == 'trendingshows':
                log("startin GetTrendingShows")
                from MiscScraper import GetTrendingShows
                passDataToSkin('TrendingShows', GetTrendingShows(), self.prop_prefix)
            elif info == 'trendingmovies':
                log("startin GetTrendingMovies")
                from MiscScraper import GetTrendingMovies
                passDataToSkin('TrendingMovies', GetTrendingMovies(), self.prop_prefix)            
            elif info == 'similarartistsinlibrary':
                passDataToSkin('SimilarArtistsInLibrary', None, self.prop_prefix)
                passDataToSkin('SimilarArtists', GetSimilarArtistsInLibrary(self.Artist_mbid), self.prop_prefix)
            elif info == 'artistevents':
                passDataToSkin('ArtistEvents', None, self.prop_prefix)
                from OnlineMusicInfo import GetEvents
             #   events = GetEvents(self.Artist_mbid)
                passDataToSkin('ArtistEvents', GetEvents(self.Artist_mbid), self.prop_prefix)     
            elif info == 'youtubesearch':
                wnd = xbmcgui.Window(Window)
                wnd.setProperty('%sSearchValue' % self.prop_prefix, self.id) # set properties 
                passDataToSkin('YoutubeSearch', None, self.prop_prefix)
                from MiscScraper import GetYoutubeSearchVideos
             #   events = GetEvents(self.Artist_mbid)
                passDataToSkin('YoutubeSearch', GetYoutubeSearchVideos(self.id,self.hd,self.orderby,self.time), self.prop_prefix)
            elif info == 'youtubeusersearch':
                passDataToSkin('YoutubeUserSearch', None, self.prop_prefix)
                from MiscScraper import GetYoutubeUserVideos
                passDataToSkin('YoutubeUserSearch', GetYoutubeUserVideos(self.id), self.prop_prefix,True)                 
            elif info == 'nearevents':
                passDataToSkin('NearEvents', None, self.prop_prefix)
                from OnlineMusicInfo import GetNearEvents
                passDataToSkin('NearEvents', GetNearEvents(self.tag,self.festivalsonly), self.prop_prefix)
            elif info == 'venueevents':
                passDataToSkin('VenueEvents', None, self.prop_prefix)
                from OnlineMusicInfo import GetVenueEvents
                passDataToSkin('VenueEvents', GetVenueEvents(self.id), self.prop_prefix)             
            elif info == 'topartistsnearevents':
                from OnlineMusicInfo import GetArtistNearEvents
                passDataToSkin('TopArtistsNearEvents', None, self.prop_prefix)
                artists = GetXBMCArtists()
                events = GetArtistNearEvents(artists["result"]["artists"][0:15])
                passDataToSkin('TopArtistsNearEvents', events, self.prop_prefix)
            elif info == 'updatexbmcdatabasewithartistmbidbg':
                from MusicBrainz import SetMusicBrainzIDsForAllArtists
                SetMusicBrainzIDsForAllArtists(False, 'forceupdate' in AdditionalParams)
            elif info == 'updatexbmcdatabasewithartistmbid':
                from MusicBrainz import SetMusicBrainzIDsForAllArtists
                SetMusicBrainzIDsForAllArtists(True, 'forceupdate' in AdditionalParams)
            elif info == 'getlocationevents':
                from OnlineMusicInfo import GetNearEvents
                wnd = xbmcgui.Window(Window)
                lat = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('lat')
                lon = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('lon')
                passDataToSkin('NearEvents', GetNearEvents(self.tag,self.festivalsonly,lat,lon), self.prop_prefix)
        if not self.silent:
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
                       
    def _init_vars(self):
        self.window = xbmcgui.Window(10000) # Home Window
        self.cleared = False
        self.musicvideos = []
        self.movies = []
        self.infos = []
        self.AlbumName = None
        self.ArtistName = None
        self.UserName = None
        self.feed = None
        self.id = None
        self.dbid = None
        self.setid = None
        self.type = False
        self.hd = ""
        self.orderby = "relevance"
        self.time = "all_time"
        self.director = ""
        self.tag = ""
        self.writer = ""
        self.studio = ""
        self.silent = True
        self.festivalsonly = False
        self.prop_prefix = ""
        self.Artist_mbid = None
        self.window.clearProperty('SongToMusicVideo.Path')

    def _parse_argv(self):
        try:
            params = dict( arg.split("=") for arg in sys.argv[1].split("&"))
        except:
            params = {}
        self.exportsettings = params.get("exportsettings", False)
        self.importsettings = params.get("importsettings", False)
        self.importextrathumb = params.get("importextrathumb", False)
        self.importextrathumbtv = params.get("importextrathumbtv", False)
        self.importextrafanart = params.get("importextrafanart", False)
        self.importextrafanarttv = params.get("importextrafanarttv", False)
        self.importallartwork = params.get("importallartwork", False)
        for arg in sys.argv:
            log(arg)
            if arg == 'script.extendedinfo':
                continue
            param = arg.lower()
            if param.startswith('info='):
                self.infos.append(param[5:])
            elif param.startswith('type='):
                self.type = (param[5:])
            elif param.startswith('tag='):
                self.tag = (param[4:])
            elif param.startswith('studio='):
                self.studio = (param[7:])
            elif param.startswith('orderby='):
                self.orderby = (param[8:])
            elif param.startswith('time='):
                self.time = (param[5:])                
            elif param.startswith('director='):
                self.director = (param[9:])
            elif param.startswith('writer='):
                self.writer = (param[7:])
            elif param.startswith('lat='):
                self.lat = (param[4:])
            elif param.startswith('lon='):
                self.lon = (param[4:])
            elif param.startswith('silent='):
                self.silent = (param[7:])
                if self.silent == "false":
                    self.silent = False
            elif param.startswith('festivalsonly='):
                self.festivalsonly = (param[14:])
            elif param.startswith('feed='):
                self.feed = param[5:]
            elif param.startswith('id='):
                self.id = param[3:]
            elif param.startswith('dbid='):
                self.dbid = param[5:]  
            elif param.startswith('setid='):
                self.setid = param[6:]  
            elif param.startswith('hd='):
                self.hd = param[3:]  
            elif param.startswith('prefix='):
                self.prop_prefix = param[7:]
                if not self.prop_prefix.endswith('.') and self.prop_prefix <> "":
                    self.prop_prefix = self.prop_prefix + '.'
            elif param.startswith('artistname='):
                self.ArtistName = arg[11:].replace('"','')
                if self.ArtistName:
                    # todo: look up local mbid first -->xbmcid for parameter
                    from MusicBrainz import GetMusicBrainzIdFromNet
                    self.Artist_mbid = GetMusicBrainzIdFromNet(self.ArtistName)
            elif param.startswith('albumname='):
                self.AlbumName = arg[10:].replace('"','')
            elif param.startswith('username='):
                self.UserName = arg[9:].replace('"','')
            elif param.startswith('tracktitle='):
                TrackTitle = arg[11:].replace('"','')
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
                                       
    def _set_detail_properties( self, movie,count):
        self.window.setProperty('Detail.Movie.%i.Path' % (count), movie["file"])
        self.window.setProperty('Detail.Movie.%i.Art(fanart)' % (count), movie["art"].get('fanart',''))
        self.window.setProperty('Detail.Movie.%i.Art(poster)' % (count), movie["art"].get('poster',''))      
                                       
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
                        _set_artist_properties(json_query)
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
            export_skinsettings()
        elif selection == 1:
            import_skinsettings()
        elif selection == 2:
            xbmc.executebuiltin("Skin.ResetSettings")
        elif selection == 3:
            AddArtToLibrary("extrathumb","Movie", "extrathumbs",extrathumb_limit)
        elif selection == 4:
            AddArtToLibrary("extrafanart","Movie", "extrafanart",extrafanart_limit)
   #     elif selection == 5:
    #        AddArtToLibrary("extrathumb","TVShow", "extrathumbs")
        elif selection == 5:
            AddArtToLibrary("extrafanart","TVShow", "extrafanart",extrafanart_limit)
        elif selection == 6:
            AddArtToLibrary("extrathumb","Movie", "extrathumbs",extrathumb_limit)
            AddArtToLibrary("extrafanart","Movie", "extrafanart",extrafanart_limit)
            AddArtToLibrary("extrafanart","TVShow", "extrafanart",extrafanart_limit)
            
if ( __name__ == "__main__" ):
    try:
        params = dict( arg.split("=") for arg in sys.argv[1].split("&"))
    except:
        params = {}
    backend = params.get("backend", False)
    if backend:
        if xbmc.getCondVisibility("IsEmpty(Window(home).Property(extendedinfo_backend_running))"):
            xbmc.executebuiltin('SetProperty(extendedinfo_backend_running,True,home)')
            log("starting daemon")
            Daemon()
    else:
        Main()
log('finished')
