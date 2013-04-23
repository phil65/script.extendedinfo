import sys
import os, time, datetime, re, random
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
        
class Main:
    def __init__( self ):
        log("version %s started" % __addonversion__ )
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
        elif self.backend and xbmc.getCondVisibility("IsEmpty(Window(home).Property(extendedinfo_backend_running))"):
            xbmc.executebuiltin('SetProperty(extendedinfo_backend_running,True,home)')
            self.run_backend()
        # only set new properties if artistid is not smaller than 0, e.g. -1
        elif self.artistid and self.artistid > -1:
            self._set_details(self.artistid)
        # else clear old properties
        elif not len(sys.argv) >1:
            self._selection_dialog()

    def _StartInfoActions(self):
        if not self.silent:
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        for info in self.infos:
            if info == 'json':
                from MiscScraper import GetYoutubeVideos
                videos = GetYoutubeVideos(self.feed,self.prop_prefix)
                passDataToSkin('RSS', videos, self.prop_prefix)
            elif info == 'similarlocal':
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
                passDataToSkin('Discography', GetArtistTopAlbums(self.Artist_mbid), self.prop_prefix,True)
            elif info == 'shouts':
                log("startin shouts")
                passDataToSkin('Shout', None, self.prop_prefix)
                from OnlineMusicInfo import GetShouts
                passDataToSkin('Shout', GetShouts(self.ArtistName,self.AlbumName), self.prop_prefix)
            elif info == 'studio':
                passDataToSkin('StudioInfo', None, self.prop_prefix)
                if self.studio:
                    log("startin companyinfo")
                    from TheMovieDB import SearchforCompany, GetCompanyInfo
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
                log("yyyy")
                log(self.setid)
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
            elif info == 'incinemaRT':
                log("start gettin InCinema info")
                from MiscScraper import GetRottenTomatoesMovies
                passDataToSkin('InCinemaMovies', GetRottenTomatoesMovies("in_theaters"), self.prop_prefix)
            elif info == 'boxoffice':
                log("start gettin boxoffice info")
                from MiscScraper import GetRottenTomatoesMovies
                passDataToSkin('BoxOffice', GetRottenTomatoesMovies("box_office"), self.prop_prefix)
            elif info == 'opening':
                log("start gettin opening info")
                from MiscScraper import GetRottenTomatoesMovies
                passDataToSkin('Opening', GetRottenTomatoesMovies("opening"), self.prop_prefix)
            elif info == 'upcoming':
                log("start gettin upcoming info")
          #      from MiscScraper import GetRottenTomatoesMovies
           #     passDataToSkin('UpcomingMovies', GetRottenTomatoesMovies("upcoming"), self.prop_prefix, True)
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('UpcomingMovies', GetMovieDBMovies("upcoming"), self.prop_prefix)
            elif info == 'incinema':
                log("start gettin InCinemaMovies info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('InCinemaMovies', GetMovieDBMovies("now_playing"), self.prop_prefix)
            elif info == 'popular':
                log("start gettin popularmovies info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('PopularMovies', GetMovieDBMovies("popular"), self.prop_prefix)
            elif info == 'toprated':
                log("start gettin InCinemaMovies info")
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('TopRatedMovies', GetMovieDBMovies("top_rated"), self.prop_prefix)          
            elif info == 'toprentals':
                log("start gettin toprentals info")
                from MiscScraper import GetRottenTomatoesMovies
                passDataToSkin('TopRentals', GetRottenTomatoesMovies("top_rentals"), self.prop_prefix)
                
                
            elif info == 'similarmovies':
                log("startin MovieDBGetSimilarMovies")
                passDataToSkin('SimilarMovies', None, self.prop_prefix)
                from TheMovieDB import GetSimilarMovies
                # MovieId = GetDatabaseID(self.id)
                if self.id:
                    MovieId = self.id
                elif self.dbid:
                    MovieId = GetDatabaseID("movie",self.dbid)
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
                    id = GetDatabaseID("movie",self.dbid)
                    log("MovieDB Id:" + str(id))
                    if id:
                        passDataToSkin('MovieLists', GetMovieLists(id), self.prop_prefix)
            elif info == 'keywords':
                passDataToSkin('Keywords', None, self.prop_prefix)
                if self.dbid:
                    log("startin Keywords")
                    from TheMovieDB import GetMovieKeywords
                    id = GetDatabaseID("movie",self.dbid)
                    log("MovieDB Id:" + str(id))
                    if id:
                        passDataToSkin('Keywords', GetMovieKeywords(id), self.prop_prefix)
                        
            elif info == 'extendedinfo':
                if self.id:
                    log("startin GetExtendedMovieInfo")
                    from TheMovieDB import GetExtendedMovieInfo
                    passHomeDataToSkin(GetExtendedMovieInfo(self.id))
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
                        id = GetDatabaseID(self.type,self.dbid)
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
             #   events = GetEvents(self.Artist_mbid,True)
                passDataToSkin('ArtistEvents', GetEvents(self.Artist_mbid), self.prop_prefix)     
            elif info == 'youtubesearch':
                passDataToSkin('YoutubeSearch', None, self.prop_prefix)
                from MiscScraper import GetYoutubeSearchVideos
             #   events = GetEvents(self.Artist_mbid,True)
                passDataToSkin('YoutubeSearch', GetYoutubeSearchVideos(self.id,self.hd,False,False), self.prop_prefix)     
            elif info == 'nearevents':
                passDataToSkin('NearEvents', None, self.prop_prefix,True)
                from OnlineMusicInfo import GetNearEvents
                passDataToSkin('NearEvents', GetNearEvents(self.type,self.festivalsonly), self.prop_prefix)
            elif info == 'venueevents':
                passDataToSkin('VenueEvents', None, self.prop_prefix)
                from OnlineMusicInfo import GetVenueEvents
                passDataToSkin('VenueEvents', GetVenueEvents(self.id), self.prop_prefix)             
            elif info == 'topartistsnearevents':
                passDataToSkin('TopArtistsNearEvents', None, self.prop_prefix)
                artists = GetXBMCArtists()
                from OnlineMusicInfo import GetArtistNearEvents
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
                lat = wnd.getProperty('%slat' % self.prop_prefix)
                lon = wnd.getProperty('%slon' % self.prop_prefix)
                passDataToSkin('NearEvents', GetNearEvents(False,False,lat,lon), self.prop_prefix)
            elif info == 'getgooglemap' or info == 'getgooglestreetviewmap':
                direction = ""
                from MiscScraper import GetGoogleMap, GetGeoCodes
                wnd = xbmcgui.Window(Window)
                if self.location == "geocode": # convert Image Coordinates to float values
                    self.lat = string2deg(self.lat)
                    self.lon = string2deg(self.lon)
                    log(self.lat)
                    log(self.lon)
                if info == 'getgooglemap':  # request normal map                   
                    image = GetGoogleMap(mode = "normal",search_string = self.location,zoomlevel = self.zoomlevel,type = self.type,aspect = self.aspect, lat=self.lat,lon=self.lon,direction = self.direction)
                    overview = ""
                else: # request streetview
                    direction = str(int(self.direction) * 18)
                    image = GetGoogleMap(mode = "streetview",search_string = self.location,aspect = self.aspect,type = self.type, lat = self.lat,lon = self.lon,zoomlevel = self.zoomlevel,direction = direction)                    
                    overview = GetGoogleMap(mode = "normal",search_string = self.location,aspect = self.aspect,type = "roadmap", lat = self.lat,lon = self.lon,zoomlevel = "17",direction = direction)                    
                wnd.setProperty('%sgooglemap' % self.prop_prefix, image) # set properties 
                wnd.setProperty('%sgooglemapoverview' % self.prop_prefix, overview)
                wnd.setProperty('%sDirection' % self.prop_prefix, str(self.direction))
                wnd.setProperty('%sDirection2' % self.prop_prefix, str(direction))
                if not self.lat or self.location=="geocode": # set properties for lat / lon (after JSON call for speed)
                    lat = self.lat
                    lon = self.lon
                    if not self.location=="geocode":
                        lat, lon = GetGeoCodes(self.location)
                    wnd.setProperty('%slat' % self.prop_prefix, str(lat))
                    wnd.setProperty('%slon' % self.prop_prefix, str(lon))
                    wnd.setProperty('%sLocation' % self.prop_prefix, "")
            elif "move" in info and "google" in info:
                from MiscScraper import GetGoogleMap
                wnd = xbmcgui.Window(Window)
                lat = wnd.getProperty('%slat' % self.prop_prefix)
                lon = wnd.getProperty('%slon' % self.prop_prefix)
                direction = int(self.direction) * 18
                if lat and lon:
                    if "street" in info:
                        from math import sin, cos, radians
                        stepsize = 0.0002
                        radiantdirection = radians(float(direction))
                        if "up" in info:
                            lat = float(lat) + cos(radiantdirection) * stepsize
                            lon = float(lon) + sin(radiantdirection) * stepsize
                        elif "down" in info:
                            lat = float(lat) - cos(radiantdirection) * stepsize
                            lon = float(lon) - sin(radiantdirection) * stepsize      
                        elif "left" in info:
                            lat = float(lat) - sin(radiantdirection) * stepsize
                            lon = float(lon) - cos(radiantdirection) * stepsize
                        elif "right" in info:
                            lat = float(lat) + sin(radiantdirection) * stepsize
                            lon = float(lon) + cos(radiantdirection) * stepsize
                    else:
                        stepsize = 200.0 / float(self.zoomlevel) / float(self.zoomlevel) / float(self.zoomlevel) / float(self.zoomlevel)
                        if "up" in info:
                            lat = float(lat) + stepsize
                        elif "down" in info:
                            lat = float(lat) - stepsize           
                        elif "left" in info:
                            lon = float(lon) - 2.0 * stepsize  
                        elif "right" in info:
                            lon = float(lon) + 2.0 * stepsize
                self.location = str(lat) + "," + str(lon)
                if "street" in info:
                    image = GetGoogleMap(mode = "streetview",search_string = self.location,zoomlevel = self.zoomlevel,type = self.type,aspect = self.aspect, lat=self.lat,lon=self.lon,direction = direction)
                    overview = GetGoogleMap(mode = "normal",search_string = self.location,aspect = self.aspect,type = "roadmap", lat = self.lat,lon = self.lon,zoomlevel = "17",direction = self.direction)                    
                else:
                    image = GetGoogleMap(mode = "normal",search_string = self.location,zoomlevel = self.zoomlevel,type = self.type,aspect = self.aspect, lat=self.lat,lon=self.lon,direction = self.direction)
                    overview = ""
                wnd.setProperty('%sgooglemap' % self.prop_prefix, image)
                wnd.setProperty('%sgooglemapoverview' % self.prop_prefix, overview)
                wnd.setProperty('%slat' % self.prop_prefix, str(lat))
                wnd.setProperty('%sDirection' % self.prop_prefix, self.direction)
                wnd.setProperty('%slon' % self.prop_prefix, str(lon))
        if not self.silent:
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            
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
        self.direction = 0
        self.aspect = "Landscape"
        self.zoomlevel = "15"
        self.location = ""
        self.director = ""
        self.writer = ""
        self.studio = ""
        self.lat = ""
        self.lon = ""
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
        self.artistid = -1
        try: self.artistid = int(params.get("artistid", "-1"))
        except: pass
        self.backend = params.get("backend", False)
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
            elif param.startswith('direction='):
                self.direction = (param[10:])
            elif param.startswith('aspect='):
                self.aspect = (param[7:])
            elif param.startswith('zoomlevel='):
                self.zoomlevel = (param[10:])
            elif param.startswith('location='):
                self.location = (param[9:])
            elif param.startswith('studio='):
                self.studio = (param[7:])
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

    def _detail_selector( self, comparator):
        self.selecteditem = xbmc.getInfoLabel("ListItem.Label")
        if (self.selecteditem != self.previousitem):
            if xbmc.getCondVisibility("!Stringcompare(ListItem.Label,..)"):
                self.previousitem = self.selecteditem
                self._clear_properties()
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
                self._clear_properties()
        xbmc.sleep(100)        
                        

    def run_backend(self):
        self._stop = False
        self.previousitem = ""
        self.previousartist = ""
        self.previoussong = ""
        self.musicvideos = create_musicvideo_list()
        self.movies = create_movie_list()
        while (not self._stop) and (not xbmc.abortRequested):
            if xbmc.getCondVisibility("Container.Content(movies) | Container.Content(sets) | Container.Content(artists) | Container.Content(albums)"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if xbmc.getCondVisibility("!IsEmpty(ListItem.DBID) + [SubString(ListItem.Path,videodb://1/7/,left)| Container.Content(artists) | Container.Content(albums)]"):
                        self._set_details(xbmc.getInfoLabel("ListItem.DBID"))
                        xbmc.sleep(100)
                    else:
                        self._clear_properties()
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
            elif xbmc.getCondVisibility("Window.IsActive(visualisation)"):
                artist = xbmc.getInfoLabel('MusicPlayer.Artist')
                if (artist != self.previousartist):
                    if artist:
                        from MusicBrainz import GetMusicBrainzIdFromNet
                        Artist_mbid = GetMusicBrainzIdFromNet(artist)
                        passDataToSkin('SimilarArtistsInLibrary', None, self.prop_prefix)
                        passDataToSkin('SimilarArtists', GetSimilarArtistsInLibrary(Artist_mbid), self.prop_prefix)
            elif xbmc.getCondVisibility('Window.IsActive(screensaver)'):
                xbmc.sleep(1000)
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
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if json_query['result'].has_key('albums'):
                        self._set_artist_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('Container.Content(albums)') or self.type == "album":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "track", "duration", "file", "lastplayed", "disc"], "sort": { "method": "label" }, "filter": {"albumid": %s} }, "id": 1}' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if "result" in json_query and json_query['result'].has_key('songs'):
                        self._set_album_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('[Container.Content(movies) + ListItem.IsFolder] | Container.Content(sets)') or self.type == "set":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "file", "year", "director", "writer","genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country"], "sort": { "order": "ascending",  "method": "year" }} },"id": 1 }' % dbid)
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if "result" in json_query and json_query['result'].has_key('setdetails'):
                        self._set_movie_properties(json_query)
                    b = datetime.datetime.now() - a
                elif xbmc.getCondVisibility('Container.Content(songs)') or self.type == "songs":
                    a = datetime.datetime.now()
                    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["artist", "file"], "sort": { "method": "artist" } }, "id": 1}')
                    json_query = unicode(json_query, 'utf-8', errors='ignore')
                    json_query = simplejson.loads(json_query)
                    self._clear_properties()
                    if "result" in json_query and json_query['result'].has_key('musicvideos'):
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
        self.window.setProperty('Set.Movies.Count', str(json_query['result']['setdetails']['limits']['total']))
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
