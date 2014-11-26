import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import urlparse
import urllib

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
sys.path.append(__resource__)

from LastFM import *
from MiscScraper import *
from TheAudioDB import *
from TheMovieDB import *
from Utils import *
from RottenTomatoes import *
from YouTube import *
from Trakt import *

homewindow = xbmcgui.Window(10000)
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
        if self.control == "plugin":
            xbmcplugin.endOfDirectory(self.handle)
        xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')

    def _StartInfoActions(self):
        if not self.silent:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
        for info in self.infos:
            ########### Images #####################
            if info == 'xkcd':
                passDataToSkin('XKCD', GetXKCDInfo(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'flickr':
                passDataToSkin('Flickr', GetFlickrImages(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'cyanide':
                passDataToSkin('CyanideHappiness', GetCandHInfo(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'dailybabes':
                passDataToSkin('DailyBabes', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('DailyBabes', GetDailyBabes(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'dailybabe':
                passDataToSkin('DailyBabe', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('DailyBabe', GetDailyBabes(single=True), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            ########### Audio #####################
            elif info == 'discography':
                passDataToSkin('Discography', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                Discography = GetDiscography(self.ArtistName)
                if len(Discography) == 0:
                    Discography = GetArtistTopAlbums(self.Artist_mbid)
                passDataToSkin('Discography', Discography, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'mostlovedtracks':
                passDataToSkin('MostLovedTracks', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('MostLovedTracks', GetMostLovedTracks(self.ArtistName), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'artistdetails':
                passDataToSkin('Discography', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('MusicVideos', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                ArtistDetails = GetArtistDetails(self.ArtistName)
                if "audiodbid" in ArtistDetails:
                    MusicVideos = GetMusicVideos(ArtistDetails["audiodbid"])
                    passDataToSkin('MusicVideos', MusicVideos, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('Discography', GetDiscography(self.ArtistName), self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passHomeDataToSkin(ArtistDetails, self.prop_prefix)
            elif info == 'albuminfo':
                if self.id:
                    AlbumDetails = GetAlbumDetails(self.id)
                    Trackinfo = GetTrackDetails(self.id)
                    passHomeDataToSkin(AlbumDetails, self.prop_prefix)
                    passDataToSkin('Trackinfo', Trackinfo, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'albumshouts':
                passDataToSkin('Shout', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.ArtistName and self.AlbumName:
                    passDataToSkin('Shout', GetAlbumShouts(self.ArtistName, self.AlbumName), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'artistshouts':
                passDataToSkin('Shout', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.ArtistName:
                    passDataToSkin('Shout', GetArtistShouts(self.ArtistName), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'topartists':
                passDataToSkin('TopArtists', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('TopArtists', GetTopArtists(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'hypedartists':
                passDataToSkin('HypedArtists', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('HypedArtists', GetHypedArtists(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            ### RottenTomatoesMovies #################################################################################
            elif info == 'intheaters':
                passDataToSkin('InTheatersMovies', GetRottenTomatoesMovies("movies/in_theaters"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'boxoffice':
                passDataToSkin('BoxOffice', GetRottenTomatoesMovies("movies/box_office"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'opening':
                passDataToSkin('Opening', GetRottenTomatoesMovies("movies/opening"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'comingsoon':
                passDataToSkin('ComingSoonMovies', GetRottenTomatoesMovies("movies/upcoming"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'toprentals':
                passDataToSkin('TopRentals', GetRottenTomatoesMovies("dvds/top_rentals"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'currentdvdreleases':
                passDataToSkin('CurrentDVDs', GetRottenTomatoesMovies("dvds/current_releases"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'newdvdreleases':
                passDataToSkin('NewDVDs', GetRottenTomatoesMovies("dvds/new_releases"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'upcomingdvds':
                passDataToSkin('UpcomingDVDs', GetRottenTomatoesMovies("dvds/upcoming"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            ### The MovieDB ##########################################################################################
            elif info == 'incinemas':
                passDataToSkin('InCinemasMovies', GetMovieDBMovies("now_playing"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'upcoming':
                passDataToSkin('UpcomingMovies', GetMovieDBMovies("upcoming"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'topratedmovies':
                passDataToSkin('TopRatedMovies', GetMovieDBMovies("top_rated"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'popularmovies':
                passDataToSkin('PopularMovies', GetMovieDBMovies("popular"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'airingtodaytvshows':
                passDataToSkin('AiringTodayTVShows', GetMovieDBTVShows("airing_today"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'onairtvshows':
                passDataToSkin('OnAirTVShows', GetMovieDBTVShows("on_the_air"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'topratedtvshows':
                passDataToSkin('TopRatedTVShows', GetMovieDBTVShows("top_rated"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'populartvshows':
                passDataToSkin('PopularTVShows', GetMovieDBTVShows("popular"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'similarmovies':
                passDataToSkin('SimilarMovies', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.id:
                    MovieId = self.id
                elif self.dbid and (int(self.dbid) > -1):
                    MovieId = GetImdbID("movie", self.dbid)
                    log("IMDBId from local DB:" + str(MovieId))
                else:
                    MovieId = ""
                if MovieId:
                    passDataToSkin('SimilarMovies', GetSimilarMovies(MovieId), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'studio':
                passDataToSkin('StudioInfo', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.studio:
                    CompanyId = SearchforCompany(self.studio)
                    passDataToSkin('StudioInfo', GetCompanyInfo(CompanyId), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'set':
                passDataToSkin('MovieSetItems', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.dbid and not "show" in str(self.type):
                    name = GetMovieSetName(self.dbid)
                    if name:
                        self.setid = SearchForSet(name)
                if self.setid:
                    SetData = GetSetMovies(self.setid)
                    if SetData:
                        passDataToSkin('MovieSetItems', SetData, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'movielists':
                passDataToSkin('MovieLists', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.dbid:
                    movieid = GetImdbID("movie", self.dbid)
                    log("MovieDB Id:" + str(movieid))
                    if movieid:
                        passDataToSkin('MovieLists', GetMovieLists(movieid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'keywords':
                passDataToSkin('Keywords', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.dbid:
                    movieid = GetImdbID("movie", self.dbid)
                    log("MovieDB Id:" + str(movieid))
                    if movieid:
                        passDataToSkin('Keywords', GetMovieKeywords(movieid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'popularpeople':
                passDataToSkin('PopularPeople', GetPopularActorList(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'extendedinfo':
                if self.id:
                    MovieId = self.id
                elif self.dbid and (int(self.dbid) > -1):
                    MovieId = GetImdbID("movie", self.dbid)
                    log("IMDBId from local DB:" + str(MovieId))
                elif self.imdbid:
                    MovieId = GetMovieDBID(self.imdbid)
                else:
                    MovieId = ""
                if MovieId:
                    from DialogVideoInfo import DialogVideoInfo
                    dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=MovieId, name=self.name)
                    dialog.doModal()
            elif info == 'extendedactorinfo':
                    from DialogActorInfo import DialogActorInfo
                    dialog = DialogActorInfo(u'script-%s-DialogInfo.xml' % __addonname__, __cwd__, id=self.id, name=self.name)
                    dialog.doModal()

            elif info == 'extendedtvinfo':
                if self.id:
                    tvshowinfo = GetTVShowInfo(self.id)
                    if tvshowinfo:
                        prettyprint(tvshowinfo)
                        passHomeDataToSkin(tvshowinfo[0], self.prop_prefix)
            elif info == 'seasoninfo':
                passDataToSkin("SeasonVideos", None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.tvshow and self.season:
                    seasoninfo, videos = GetSeasonInfo(self.tvshow, self.season)
                    passHomeDataToSkin(seasoninfo, self.prop_prefix)
                    passDataToSkin("SeasonVideos", videos, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'directormovies':
                passDataToSkin('DirectorMovies', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.director:
                    directorid = GetPersonID(self.director)
                    if directorid:
                        passDataToSkin('DirectorMovies', GetDirectorMovies(directorid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'writermovies':
                passDataToSkin('WriterMovies', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.writer and not self.writer.split(" / ")[0] == self.director.split(" / ")[0]:
                    writerid = GetPersonID(self.writer)
                    if writerid:
                        passDataToSkin('WriterMovies', GetDirectorMovies(writerid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'similarmoviestrakt':
                passDataToSkin('SimilarTrakt', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if (self.id or self.dbid):
                    if self.dbid:
                        movieid = GetImdbID("movie", self.dbid)
                    else:
                        movieid = self.id
                    passDataToSkin('SimilarMovies', GetSimilarTrakt("movie", movieid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'similartvshowstrakt':
                passDataToSkin('SimilarTrakt', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if (self.id or self.dbid):
                    if self.dbid:
                        if self.type == "episode":
                            tvshowid = GetImdbIDfromEpisode(self.dbid)
                        else:
                            tvshowid = GetImdbID("tvshow", self.dbid)
                    else:
                        tvshowid = self.id
                    passDataToSkin('SimilarTVShows', GetSimilarTrakt("show", tvshowid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'airingshows':
                passDataToSkin('AiringShows', GetTraktCalendarShows("shows"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'premiereshows':
                passDataToSkin('PremiereShows', GetTraktCalendarShows("premieres"), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'trendingshows':
                passDataToSkin('TrendingShows', GetTrendingShows(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'trendingmovies':
                passDataToSkin('TrendingMovies', GetTrendingMovies(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'similarartistsinlibrary':
                passDataToSkin('SimilarArtists', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.Artist_mbid:
                    passDataToSkin('SimilarArtists', GetSimilarArtistsInLibrary(self.Artist_mbid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'artistevents':
                passDataToSkin('ArtistEvents', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.Artist_mbid:
                    passDataToSkin('ArtistEvents', GetEvents(self.Artist_mbid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'youtubesearch':
                homewindow.setProperty('%sSearchValue' % self.prop_prefix, self.id)  # set properties
                passDataToSkin('YoutubeSearch', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.id:
                    passDataToSkin('YoutubeSearch', GetYoutubeSearchVideos(self.id, self.hd, self.orderby), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'youtubeplaylist':
                passDataToSkin('YoutubePlaylist', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.id:
                    passDataToSkin('YoutubePlaylist', GetYoutubePlaylistVideos(self.id), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'youtubeusersearch':
                passDataToSkin('YoutubeUserSearch', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.id:
                    passDataToSkin('YoutubeUserSearch', GetYoutubeUserVideos(self.id), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'nearevents':
                passDataToSkin('NearEvents', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('NearEvents', GetNearEvents(self.tag, self.festivalsonly, self.lat, self.lon, self.location, self.distance), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'trackinfo':
                homewindow.setProperty('%sSummary' % self.prop_prefix, "")  # set properties
                if self.ArtistName and self.TrackName:
                    TrackInfo = GetTrackInfo(self.ArtistName, self.TrackName)
                    homewindow.setProperty('%sSummary' % self.prop_prefix, TrackInfo["summary"])  # set properties
            elif info == 'venueevents':
                passDataToSkin('VenueEvents', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                if self.location:
                    self.id = GetVenueID(self.location)
                if self.id:
                    passDataToSkin('VenueEvents', GetVenueEvents(self.id), self.prop_prefix, self.window, self.control, self.handle, self.limit)
                else:
                    Notify("Error", "Could not find venue")
            elif info == 'topartistsnearevents':
                passDataToSkin('TopArtistsNearEvents', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                artists = GetXBMCArtists()
                events = GetArtistNearEvents(artists["result"]["artists"][0:49])
                passDataToSkin('TopArtistsNearEvents', events, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'channels':
                channels = create_channel_list()
                prettyprint(channels)
            elif info == 'favourites':
                if self.id:
                    favourites = GetFavouriteswithType(self.id)
                    Notify("here")
                else:
                    favourites = GetFavourites()
                    homewindow.setProperty('favourite.count', str(len(favourites)))
                    if len(favourites) > 0:
                        homewindow.setProperty('favourite.1.name', favourites[-1]["Label"])
                passDataToSkin('Favourites', favourites, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'json':
                passDataToSkin('RSS', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                videos = GetYoutubeVideos(self.feed, self.prop_prefix)
                passDataToSkin('RSS', videos, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'similarlocal' and self.dbid:
                passDataToSkin('SimilarLocalMovies', None, self.prop_prefix, self.window, self.control, self.handle, self.limit)
                passDataToSkin('SimilarLocalMovies', GetSimilarFromOwnLibrary(self.dbid), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'iconpanel':
                passDataToSkin('IconPanel', GetIconPanel(1), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'weather':
                passDataToSkin('WeatherImages', GetWeatherImages(), self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'updatexbmcdatabasewithartistmbidbg':
                SetMusicBrainzIDsForAllArtists(False, False)
            elif info == 'setfocus':
                xbmc.executebuiltin("SetFocus(22222)")
            elif info == 'playliststats':
                GetPlaylistStats(self.id)
            elif info == "sortletters":
                listitems = GetSortLetters(self.path, self.id)
                passDataToSkin('SortLetters', listitems, self.prop_prefix, self.window, self.control, self.handle, self.limit)
            elif info == 'slideshow':
                windowid = xbmcgui.getCurrentWindowId()
                Window = xbmcgui.Window(windowid)
                focusid = Window.getFocusId()
                itemlist = Window.getFocus()
                numitems = itemlist.getSelectedPosition()
                log("items:" + str(numitems))
                for i in range(0, numitems):
                    Notify(item.getProperty("Image"))
            elif info == 'action':
                xbmc.executebuiltin(self.id)
            elif info == 'playtrailer':
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                if self.id:
                    MovieId = self.id
                elif self.dbid and (int(self.dbid) > -1):
                    MovieId = GetImdbID("movie", self.dbid)
                    log("MovieDBID from local DB:" + str(MovieId))
                elif self.imdbid:
                    MovieId = GetMovieDBID(self.imdbid)
                else:
                    MovieId = ""
                if MovieId:
                    movie, actors = GetExtendedMovieInfo(MovieId)
                    xbmc.executebuiltin("Dialog.Close(busydialog)")
                    if "Trailer" is not "":
                        xbmc.executebuiltin("PlayMedia(" + movie["Trailer"] + ")")
                        self.control = ""  # workaround to avoid breaking PlayMedia
                    else:
                        Notify("Error", "No Trailer available")
            elif info == 'updatexbmcdatabasewithartistmbid':
                SetMusicBrainzIDsForAllArtists(True, False)

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
        self.imdbid = None
        self.setid = None
        self.type = False
        self.hd = ""
        self.orderby = "relevance"
        self.time = "all_time"
        self.director = ""
        self.tag = ""
        self.name = ""
        self.path = ""
        self.tvshow = ""
        self.season = ""
        self.writer = ""
        self.studio = ""
        self.lat = ""
        self.lon = ""
        self.infodialog = False
        self.limit = False
        self.location = ""
        self.distance = ""
        self.silent = True
        self.handle = None
        self.festivalsonly = False
        self.prop_prefix = ""
        self.Artist_mbid = None
        self.pluginmode = False
        self.window.clearProperty('SongToMusicVideo.Path')

    def _build_url(self, query):
        return base_url + '?' + urllib.urlencode(query)

    def _parse_argv(self):
        if sys.argv[0] == 'plugin://script.extendedinfo/':
            self.pluginmode = True
            args = sys.argv[2][1:].split("&&")
            dict_args = urlparse.parse_qs(sys.argv[2][1:])
            self.handle = int(sys.argv[1])
            base_url = sys.argv[0]
            self.control = "plugin"
            params = {}
        else:
            args = sys.argv
            try:
                params = dict(arg.split("=") for arg in sys.argv[1].split("&"))
            except:
                params = {}
        if not self.silent:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.exportsettings = params.get("exportsettings", False)
        self.importsettings = params.get("importsettings", False)
        self.importextrathumb = params.get("importextrathumb", False)
        self.importextrathumbtv = params.get("importextrathumbtv", False)
        self.importextrafanart = params.get("importextrafanart", False)
        self.importextrafanarttv = params.get("importextrafanarttv", False)
        self.importallartwork = params.get("importallartwork", False)
        for arg in args:
            log(arg)
            if arg == 'script.extendedinfo':
                continue
            param = arg.replace('"', '').replace("'", " ")
            log(param)
            if param.startswith('info='):
                self.infos.append(param[5:])
            elif param.startswith('type='):
                self.type = param[5:]
            elif param.startswith('tag='):
                self.tag = param[4:]
            elif param.startswith('studio='):
                self.studio = param[7:]
            elif param.startswith('orderby='):
                self.orderby = param[8:]
            elif param.startswith('time='):
                self.time = param[5:]
            elif param.startswith('director='):
                self.director = param[9:]
            elif param.startswith('writer='):
                self.writer = param[7:]
            elif param.startswith('lat='):
                self.lat = param[4:]
            elif param.startswith('lon='):
                self.lon = param[4:]
            elif param.startswith('location='):
                self.location = param[9:]
            elif param.startswith('distance='):
                self.distance = param[9:]
            elif param.startswith('silent='):
                self.silent = param[7:]
                if self.silent == "false":
                    self.silent = False
            elif param.startswith('festivalsonly='):
                self.festivalsonly = param[14:]
            elif param.startswith('feed='):
                self.feed = param[5:]
            elif param.startswith('name='):
                self.name = param[5:]
            elif param.startswith('path='):
                self.path = param[5:]
            elif param.startswith('id='):
                self.id = param[3:]
            elif param.startswith('infodialog='):
                if param[11:].lower() == "true":
                    self.infodialog = True
            elif param.startswith('dbid='):
                self.dbid = param[5:]
            elif param.startswith('imdbid='):
                self.imdbid = param[7:]
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
                if (not self.prop_prefix.endswith('.')) and (self.prop_prefix is not ""):
                    self.prop_prefix = self.prop_prefix + '.'
            elif param.startswith('artistname='):
                self.ArtistName = arg[11:].split(" feat. ")[0].strip()
                if self.ArtistName:
                    # todo: look up local mbid first -->xbmcid for parameter
                    self.Artist_mbid = GetMusicBrainzIdFromNet(self.ArtistName)
            elif param.startswith('albumname='):
                self.AlbumName = arg[10:].strip()
            elif param.startswith('trackname='):
                self.TrackName = arg[10:].strip()
            elif param.startswith('username='):
                self.UserName = arg[9:].strip()
            elif param.startswith('limit='):
                self.limit = int(arg[6:])
            elif param.startswith('window='):
                if arg[7:] == "currentdialog":
                    xbmc.sleep(300)
                    self.window = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
                elif arg[7:] == "current":
                    xbmc.sleep(300)
                    self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                else:
                    self.window = xbmcgui.Window(int(arg[7:]))
            elif param.startswith('control='):
                self.control = int(arg[8:])
        if not self.silent:
            xbmc.executebuiltin("Dialog.Close(busydialog)")

if (__name__ == "__main__"):
    Main()
log('finished')
