import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson


__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

TrackTitle = None
AdditionalParams = []
wnd = xbmcgui.Window(10000)
extrathumb_limit = 4
extrafanart_limit = 10
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % __addonid__).decode("utf-8"))
Skin_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmc.getSkinDir()).decode("utf-8"))


class Main:

    def __init__(self):
        log("version %s started" % __addonversion__)
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
            AddArtToLibrary("extrathumb", "Movie", "extrathumbs", extrathumb_limit, True)
        elif self.importextrafanart:
            AddArtToLibrary("extrafanart", "Movie", "extrafanart", extrafanart_limit, True)
   #     elif self.importextrathumbtv:
  #          AddArtToLibrary("extrathumb","TVShow","extrathumbs")
        elif self.importextrafanarttv:
            AddArtToLibrary("extrafanart", "TVShow", "extrafanart", extrafanart_limit, True)
        elif self.importallartwork:
            AddArtToLibrary("extrathumb", "Movie", "extrathumbs", extrathumb_limit, True)
            AddArtToLibrary("extrafanart", "Movie", "extrafanart", extrafanart_limit, True)
            AddArtToLibrary("extrafanart", "TVShow", "extrafanart", extrafanart_limit, True)
        elif not len(sys.argv) > 1:
            self._selection_dialog()
        xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')

    def _StartInfoActions(self):
        if not self.silent:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
        for info in self.infos:
            if info == 'json':
                from MiscScraper import GetYoutubeVideos
                videos = GetYoutubeVideos(self.feed, self.prop_prefix)
                passDataToSkin('RSS', videos, self.prop_prefix, self.window, self.control)
            elif info == 'similarlocal' and self.dbid:
                passDataToSkin('SimilarLocalMovies', None, self.prop_prefix, self.window, self.control)
                passDataToSkin('SimilarLocalMovies', GetSimilarFromOwnLibrary(self.dbid), self.prop_prefix, self.window, self.control)
            elif info == 'xkcd':
                from MiscScraper import GetXKCDInfo
                passDataToSkin('XKCD', GetXKCDInfo(), self.prop_prefix, self.window, self.control)
            elif info == 'flickr':
                from MiscScraper import GetFlickrImages
                passDataToSkin('Flickr', GetFlickrImages(), self.prop_prefix, self.window, self.control)
            elif info == 'discography':
                passDataToSkin('Discography', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetArtistTopAlbums
                passDataToSkin('Discography', GetArtistTopAlbums(self.Artist_mbid), self.prop_prefix, self.window, self.control)
            elif info == 'mostlovedtracks':
                passDataToSkin('MostLovedTracks', None, self.prop_prefix, self.window, self.control)
                from TheAudioDB import GetMostLovedTracks
                passDataToSkin('MostLovedTracks', GetMostLovedTracks(self.ArtistName), self.prop_prefix, self.window, self.control)
            elif info == 'artistdetails':
                passDataToSkin('Discography', None, self.prop_prefix, self.window, self.control)
                passDataToSkin('MusicVideos', None, self.prop_prefix, self.window, self.control)
                from TheAudioDB import GetDiscography, GetArtistDetails, GetMusicVideos
                ArtistDetails = GetArtistDetails(self.ArtistName)
                if "audiodbid" in ArtistDetails:
                    MusicVideos = GetMusicVideos(ArtistDetails["audiodbid"])
                    passDataToSkin('MusicVideos', MusicVideos, self.prop_prefix, self.window, self.control)
            #    GetAudioDBData("search.php?s=Blur")
            #    from TheAudioDB import GetArtistTopAlbums
                passDataToSkin('Discography', GetDiscography(self.ArtistName), self.prop_prefix, self.window, self.control)
                passHomeDataToSkin(ArtistDetails)
            elif info == 'albuminfo':
                passHomeDataToSkin(None)
                from TheAudioDB import GetAlbumDetails, GetTrackDetails
                if self.id:
                    AlbumDetails = GetAlbumDetails(self.id)
                    Trackinfo = GetTrackDetails(self.id)
              #      prettyprint(AlbumDetails)
                    passHomeDataToSkin(AlbumDetails)
                    passDataToSkin('Trackinfo', Trackinfo, self.prop_prefix, self.window, self.control)
            elif info == 'albumshouts':
                passDataToSkin('Shout', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetAlbumShouts
                if self.ArtistName and self.AlbumName:
                    passDataToSkin('Shout', GetAlbumShouts(self.ArtistName, self.AlbumName), self.prop_prefix, self.window, self.control)
            elif info == 'artistshouts':
                passDataToSkin('Shout', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetArtistShouts
                if self.ArtistName:
                    passDataToSkin('Shout', GetArtistShouts(self.ArtistName), self.prop_prefix, self.window, self.control)
            elif info == 'studio':
                passDataToSkin('StudioInfo', None, self.prop_prefix, self.window, self.control)
                if self.studio:
                    from TheMovieDB import SearchforCompany, GetCompanyInfo
                    if self.studio:
                        CompanyId = SearchforCompany(self.studio)
                        passDataToSkin('StudioInfo', GetCompanyInfo(CompanyId), self.prop_prefix, self.window, self.control)
            elif info == 'set':
                passDataToSkin('MovieSetItems', None, self.prop_prefix, self.window, self.control)
                if self.dbid and not "show" in str(self.type):
                    from TheMovieDB import SearchForSet
                    name = GetMovieSetName(self.dbid)
                    if name:
                        self.setid = SearchForSet(name)
                if self.setid:
                    from TheMovieDB import GetSetMovies
                    SetData = GetSetMovies(self.setid)
                    if SetData:
                        passDataToSkin('MovieSetItems', SetData, self.prop_prefix, self.window, self.control)
            elif info == 'topartists':
                passDataToSkin('TopArtists', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetTopArtists
                passDataToSkin('TopArtists', GetTopArtists(), self.prop_prefix, self.window, self.control)
            elif info == 'cyanide':
                from MiscScraper import GetCandHInfo
                passDataToSkin('CyanideHappiness', GetCandHInfo(), self.prop_prefix, self.window, self.control)

            ### RottenTomatoesMovies #################################################################################
            elif info == 'intheaters':
                from RottenTomatoes import GetRottenTomatoesMoviesInTheaters
                passDataToSkin('InTheatersMovies', GetRottenTomatoesMoviesInTheaters("in_theaters"), self.prop_prefix, self.window, self.control)
            elif info == 'boxoffice':
                from RottenTomatoes import GetRottenTomatoesMoviesBoxOffice
                passDataToSkin('BoxOffice', GetRottenTomatoesMoviesBoxOffice("box_office"), self.prop_prefix, self.window, self.control)
            elif info == 'opening':
                from RottenTomatoes import GetRottenTomatoesMoviesOpening
                passDataToSkin('Opening', GetRottenTomatoesMoviesOpening("opening"), self.prop_prefix, self.window, self.control)
            elif info == 'comingsoon':
                from RottenTomatoes import GetRottenTomatoesMoviesComingSoon
                passDataToSkin('ComingSoonMovies', GetRottenTomatoesMoviesComingSoon("upcoming"), self.prop_prefix, self.window, self.control)
            elif info == 'toprentals':
                from RottenTomatoes import GetRottenTomatoesMovies
                passDataToSkin('TopRentals', GetRottenTomatoesMovies("top_rentals"), self.prop_prefix, self.window, self.control)

            ### The MovieDB ##########################################################################################
            elif info == 'incinemas':
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('InCinemasMovies', GetMovieDBMovies("now_playing"), self.prop_prefix, self.window, self.control)
            elif info == 'upcoming':
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('UpcomingMovies', GetMovieDBMovies("upcoming"), self.prop_prefix, self.window, self.control)
            elif info == 'topratedmovies':
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('TopRatedMovies', GetMovieDBMovies("top_rated"), self.prop_prefix, self.window, self.control)
            elif info == 'popularmovies':
                from TheMovieDB import GetMovieDBMovies
                passDataToSkin('PopularMovies', GetMovieDBMovies("popular"), self.prop_prefix, self.window, self.control)

            elif info == 'airingtodaytvshows':
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('AiringTodayTVShows', GetMovieDBTVShows("airing_today"), self.prop_prefix, self.window, self.control)
            elif info == 'onairtvshows':
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('OnAirTVShows', GetMovieDBTVShows("on_the_air"), self.prop_prefix, self.window, self.control)
            elif info == 'topratedtvshows':
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('TopRatedTVShows', GetMovieDBTVShows("top_rated"), self.prop_prefix, self.window, self.control)
            elif info == 'populartvshows':
                from TheMovieDB import GetMovieDBTVShows
                passDataToSkin('PopularTVShows', GetMovieDBTVShows("popular"), self.prop_prefix, self.window, self.control)
            elif info == 'similarmovies':
                passDataToSkin('SimilarMovies', None, self.prop_prefix, self.window, self.control)
                from TheMovieDB import GetSimilarMovies
                # MovieId = GetImdbID(self.id)
                if self.id:
                    MovieId = self.id
                elif self.dbid:
                    MovieId = GetImdbID("movie", self.dbid)
                    log("IMDBId from local DB:" + str(MovieId))
                else:
                    MovieId = ""
                if MovieId:
                    passDataToSkin('SimilarMovies', GetSimilarMovies(MovieId), self.prop_prefix, self.window, self.control)
            elif info == 'movielists':
                passDataToSkin('MovieLists', None, self.prop_prefix, self.window, self.control)
                if self.dbid:
                    from TheMovieDB import GetMovieLists
                    id = GetImdbID("movie", self.dbid)
                    log("MovieDB Id:" + str(id))
                    if id:
                        passDataToSkin('MovieLists', GetMovieLists(id), self.prop_prefix, self.window, self.control)
            elif info == 'keywords':
                passDataToSkin('Keywords', None, self.prop_prefix, self.window, self.control)
                if self.dbid:
                    from TheMovieDB import GetMovieKeywords
                    id = GetImdbID("movie", self.dbid)
                    log("MovieDB Id:" + str(id))
                    if id:
                        passDataToSkin('Keywords', GetMovieKeywords(id), self.prop_prefix, self.window, self.control)
            elif info == 'extendedinfo':
                log("startin GetExtendedMovieInfo")
                if self.id:
                    MovieId = self.id
                elif self.dbid:
                    MovieId = GetImdbID("movie", self.dbid)
                    log("IMDBId from local DB:" + str(MovieId))
                else:
                    MovieId = ""
                if MovieId:
                    from TheMovieDB import GetExtendedMovieInfo
                    passHomeDataToSkin(GetExtendedMovieInfo(MovieId))
            elif info == 'extendedtvinfo':
                if self.id:
                    from MiscScraper import GetTVShowInfo
                    passHomeDataToSkin(GetTVShowInfo(self.id)[0])
            elif info == 'seasoninfo':
                if self.tvshow and self.season:
                    from TheMovieDB import GetSeasonInfo
                    passHomeDataToSkin(GetSeasonInfo(self.tvshow, self.season))
            elif info == 'directormovies':
                passDataToSkin('DirectorMovies', None, self.prop_prefix, self.window, self.control)
                if self.director:
                    from TheMovieDB import GetDirectorMovies, GetPersonID
                    directorid = GetPersonID(self.director)
                    if directorid:
                        passDataToSkin('DirectorMovies', GetDirectorMovies(directorid), self.prop_prefix, self.window, self.control)
            elif info == 'writermovies':
                passDataToSkin('WriterMovies', None, self.prop_prefix, self.window, self.control)
                if self.writer and not self.writer.split(" / ")[0] == self.director.split(" / ")[0]:
                    from TheMovieDB import GetDirectorMovies, GetPersonID
                    writerid = GetPersonID(self.writer)
                    if writerid:
                        passDataToSkin('WriterMovies', GetDirectorMovies(writerid), self.prop_prefix, self.window, self.control)
            elif info == 'similar':
                passDataToSkin('SimilarMovies', None, self.prop_prefix, self.window, self.control)
                from Trakt import GetSimilarTrakt
                if self.type and (self.id or self.dbid):
                    if self.dbid:
                        id = GetImdbID(self.type, self.dbid)
                    else:
                        id = self.id
                    passDataToSkin('SimilarMovies', GetSimilarTrakt(self.type, id), self.prop_prefix, self.window, self.control)
            elif info == 'airingshows':
                from Trakt import GetTraktCalendarShows
                passDataToSkin('AiringShows', GetTraktCalendarShows("shows"), self.prop_prefix, self.window, self.control)
            elif info == 'premiereshows':
                from Trakt import GetTraktCalendarShows
                passDataToSkin('PremiereShows', GetTraktCalendarShows("premieres"), self.prop_prefix, self.window, self.control)
            elif info == 'trendingshows':
                from Trakt import GetTrendingShows
                passDataToSkin('TrendingShows', GetTrendingShows(), self.prop_prefix, self.window, self.control)
            elif info == 'trendingmovies':
                from Trakt import GetTrendingMovies
                passDataToSkin('TrendingMovies', GetTrendingMovies(), self.prop_prefix, self.window, self.control, True)
            elif info == 'similarartistsinlibrary':
                passDataToSkin('SimilarArtists', None, self.prop_prefix, self.window, self.control)
                passDataToSkin('SimilarArtists', GetSimilarArtistsInLibrary(self.Artist_mbid), self.prop_prefix, self.window, self.control)
            elif info == 'artistevents':
                passDataToSkin('ArtistEvents', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetEvents
                passDataToSkin('ArtistEvents', GetEvents(self.Artist_mbid), self.prop_prefix, self.window, self.control)
            elif info == 'youtubesearch':
                wnd.setProperty('%sSearchValue' % self.prop_prefix, self.id)  # set properties
                passDataToSkin('YoutubeSearch', None, self.prop_prefix, self.window, self.control)
                from MiscScraper import GetYoutubeSearchVideos
                passDataToSkin('YoutubeSearch', GetYoutubeSearchVideos(self.id, self.hd, self.orderby, self.time), self.prop_prefix, self.window, self.control)
            elif info == 'youtubeusersearch':
                passDataToSkin('YoutubeUserSearch', None, self.prop_prefix, self.window, self.control)
                from MiscScraper import GetYoutubeUserVideos
                passDataToSkin('YoutubeUserSearch', GetYoutubeUserVideos(self.id), self.prop_prefix, self.window, self.control)
            elif info == 'nearevents':
                passDataToSkin('NearEvents', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetNearEvents
                passDataToSkin('NearEvents', GetNearEvents(self.tag, self.festivalsonly), self.prop_prefix, self.window, self.control)
            elif info == 'trackinfo':
                passDataToSkin('TrackInfo', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetTrackInfo
                TrackInfo = GetTrackInfo(self.ArtistName, self.TrackName)
                wnd.setProperty('%sSummary' % self.prop_prefix, TrackInfo["summary"])  # set properties
            elif info == 'venueevents':
                passDataToSkin('VenueEvents', None, self.prop_prefix, self.window, self.control)
                from LastFM import GetVenueEvents
                passDataToSkin('VenueEvents', GetVenueEvents(self.id), self.prop_prefix, self.window, self.control)
            elif info == 'topartistsnearevents':
                from MiscScraper import GetArtistNearEvents
                passDataToSkin('TopArtistsNearEvents', None, self.prop_prefix, self.window, self.control)
                artists = GetXBMCArtists()
                events = GetArtistNearEvents(artists["result"]["artists"][0:49])
                passDataToSkin('TopArtistsNearEvents', events, self.prop_prefix, self.window, self.control)
            elif info == 'updatexbmcdatabasewithartistmbidbg':
                from MusicBrainz import SetMusicBrainzIDsForAllArtists
                SetMusicBrainzIDsForAllArtists(False, 'forceupdate' in AdditionalParams)
            elif info == 'updatexbmcdatabasewithartistmbid':
                from MusicBrainz import SetMusicBrainzIDsForAllArtists
                SetMusicBrainzIDsForAllArtists(True, 'forceupdate' in AdditionalParams)
            elif info == 'getlocationevents':
                from LastFM import GetNearEvents
                lat = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('lat')
                lon = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('lon')
                passDataToSkin('NearEvents', GetNearEvents(self.tag, self.festivalsonly, lat, lon), self.prop_prefix, self.window, self.control)
        if not self.silent:
            xbmc.executebuiltin("Dialog.Close(busydialog)")

    def _init_vars(self):
        self.window = xbmcgui.Window(10000)  # Home Window
        self.control = None
        self.cleared = False
        self.musicvideos = []
        self.movies = []
        self.infos = []
        self.AlbumName = None
        self.ArtistName = None
        self.TrackName = None
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
        self.tvshow = ""
        self.season = ""
        self.writer = ""
        self.studio = ""
        self.silent = True
        self.festivalsonly = False
        self.prop_prefix = ""
        self.Artist_mbid = None
        self.window.clearProperty('SongToMusicVideo.Path')

    def _parse_argv(self):
        try:
            params = dict(arg.split("=") for arg in sys.argv[1].split("&"))
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
            elif param.startswith('tvshow='):
                self.tvshow = param[7:]
            elif param.startswith('season='):
                self.season = param[7:]
            elif param.startswith('prefix='):
                self.prop_prefix = param[7:]
                if not self.prop_prefix.endswith('.') and self.prop_prefix is not "":
                    self.prop_prefix = self.prop_prefix + '.'
            elif param.startswith('artistname='):
                self.ArtistName = arg[11:].replace('"', '')
                if self.ArtistName:
                    # todo: look up local mbid first -->xbmcid for parameter
                    from MusicBrainz import GetMusicBrainzIdFromNet
                    self.Artist_mbid = GetMusicBrainzIdFromNet(self.ArtistName)
            elif param.startswith('albumname='):
                self.AlbumName = arg[10:].replace('"', '')
            elif param.startswith('trackname='):
                self.TrackName = arg[10:].replace('"', '')
            elif param.startswith('username='):
                self.UserName = arg[9:].replace('"', '')
            elif param.startswith('window='):
                self.window = xbmcgui.Window(int(arg[7:]))
            elif param.startswith('control='):
                self.control = int(arg[8:])
            elif param.startswith('setuplocation'):
                settings = xbmcaddon.Addon(id='script.extendedinfo')
                country = settings.getSetting('country')
                city = settings.getSetting('city')
                log('stored country/city: %s/%s' % (country, city))
                kb = xbmc.Keyboard('', __language__(32013) + ":")
                kb.doModal()
                country = kb.getText()
                kb = xbmc.Keyboard('', __language__(32012) + ":")
                kb.doModal()
                city = kb.getText()
                log('country/city: %s/%s' % (country, city))
                settings.setSetting('location_method', 'country_city')
                settings.setSetting('country', country)
                settings.setSetting('city', city)
                log('done with settings')
            else:
                AdditionalParams.append(param)

    def _selection_dialog(self):
        modeselect = []
        modeselect.append(__language__(32001))
        modeselect.append(__language__(32002))
        modeselect.append(__language__(32003))
        modeselect.append(__language__(32014))
        modeselect.append(__language__(32015))
     #   modeselect.append( __language__(32014) + " (TV)" )
        modeselect.append(__language__(32015) + " (TV)")
        modeselect.append("Update All")
        dialogSelection = xbmcgui.Dialog()
        selection = dialogSelection.select(__language__(32004), modeselect)
        if selection == 0:
            export_skinsettings()
        elif selection == 1:
            import_skinsettings()
        elif selection == 2:
            xbmc.executebuiltin("Skin.ResetSettings")
        elif selection == 3:
            AddArtToLibrary("extrathumb", "Movie", "extrathumbs", extrathumb_limit)
        elif selection == 4:
            AddArtToLibrary("extrafanart", "Movie", "extrafanart", extrafanart_limit)
   #     elif selection == 5:
    #        AddArtToLibrary("extrathumb","TVShow", "extrathumbs")
        elif selection == 5:
            AddArtToLibrary("extrafanart", "TVShow", "extrafanart", extrafanart_limit)
        elif selection == 6:
            AddArtToLibrary("extrathumb", "Movie", "extrathumbs", extrathumb_limit)
            AddArtToLibrary("extrafanart", "Movie", "extrafanart", extrafanart_limit)
            AddArtToLibrary("extrafanart", "TVShow", "extrafanart", extrafanart_limit)

if (__name__ == "__main__"):
    Main()
log('finished')
