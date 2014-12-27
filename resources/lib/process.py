from LastFM import *
from MiscScraper import *
from TheAudioDB import *
from TheMovieDB import *
from Utils import *
from RottenTomatoes import *
from YouTube import *
from Trakt import *
homewindow = xbmcgui.Window(10000)
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % addon_id).decode("utf-8"))
Skin_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmc.getSkinDir()).decode("utf-8"))


def StartInfoActions(infos, params):
    for info in infos:
        ########### Images #####################
        if info == 'xkcd':
            passListToSkin('XKCD', GetXKCDInfo(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'flickr':
            passListToSkin('Flickr', GetFlickrImages(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'cyanide':
            passListToSkin('CyanideHappiness', GetCandHInfo(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'dailybabes':
            passListToSkin('DailyBabes', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('DailyBabes', GetDailyBabes(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'dailybabe':
            passListToSkin('DailyBabe', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('DailyBabe', GetDailyBabes(single=True), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        ########### Audio #####################
        elif info == 'discography':
            passListToSkin('Discography', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            Discography = GetDiscography(params["artistname"])
            if len(Discography) == 0:
                Discography = GetArtistTopAlbums(params["artist_mbid"])
            passListToSkin('Discography', Discography, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'mostlovedtracks':
            passListToSkin('MostLovedTracks', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('MostLovedTracks', GetMostLovedTracks(params["artistname"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'artistdetails':
            passListToSkin('Discography', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('MusicVideos', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            ArtistDetails = GetArtistDetails(params["artistname"])
            if "audiodbid" in ArtistDetails:
                MusicVideos = GetMusicVideos(ArtistDetails["audiodbid"])
                passListToSkin('MusicVideos', MusicVideos, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('Discography', GetDiscography(params["artistname"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passDictToSkin(ArtistDetails, params.get("prefix", ""))
        elif info == 'albuminfo':
            if params.get("id", ""):
                AlbumDetails = GetAlbumDetails(params.get("id", ""))
                Trackinfo = GetTrackDetails(params.get("id", ""))
                passDictToSkin(AlbumDetails, params.get("prefix", ""))
                passListToSkin('Trackinfo', Trackinfo, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'albumshouts':
            passListToSkin('Shout', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["artistname"] and params["albumname"]:
                passListToSkin('Shout', GetAlbumShouts(params["artistname"], params["albumname"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'artistshouts':
            passListToSkin('Shout', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["artistname"]:
                passListToSkin('Shout', GetArtistShouts(params["artistname"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'topartists':
            passListToSkin('TopArtists', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('TopArtists', GetTopArtists(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'hypedartists':
            passListToSkin('HypedArtists', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('HypedArtists', GetHypedArtists(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        ### RottenTomatoesMovies #################################################################################
        elif info == 'intheaters':
            passListToSkin('InTheatersMovies', GetRottenTomatoesMovies("movies/in_theaters"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'boxoffice':
            passListToSkin('BoxOffice', GetRottenTomatoesMovies("movies/box_office"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'opening':
            passListToSkin('Opening', GetRottenTomatoesMovies("movies/opening"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'comingsoon':
            passListToSkin('ComingSoonMovies', GetRottenTomatoesMovies("movies/upcoming"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'toprentals':
            passListToSkin('TopRentals', GetRottenTomatoesMovies("dvds/top_rentals"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'currentdvdreleases':
            passListToSkin('CurrentDVDs', GetRottenTomatoesMovies("dvds/current_releases"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'newdvdreleases':
            passListToSkin('NewDVDs', GetRottenTomatoesMovies("dvds/new_releases"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'upcomingdvds':
            passListToSkin('UpcomingDVDs', GetRottenTomatoesMovies("dvds/upcoming"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        ### The MovieDB ##########################################################################################
        elif info == 'incinemas':
            passListToSkin('InCinemasMovies', GetMovieDBMovies("now_playing"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'upcoming':
            passListToSkin('UpcomingMovies', GetMovieDBMovies("upcoming"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'topratedmovies':
            passListToSkin('TopRatedMovies', GetMovieDBMovies("top_rated"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'popularmovies':
            passListToSkin('PopularMovies', GetMovieDBMovies("popular"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'airingtodaytvshows':
            passListToSkin('AiringTodayTVShows', GetMovieDBTVShows("airing_today"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'onairtvshows':
            passListToSkin('OnAirTVShows', GetMovieDBTVShows("on_the_air"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'topratedtvshows':
            passListToSkin('TopRatedTVShows', GetMovieDBTVShows("top_rated"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'populartvshows':
            passListToSkin('PopularTVShows', GetMovieDBTVShows("popular"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'similarmovies':
            passListToSkin('SimilarMovies', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params.get("id", ""):
                MovieId = params.get("id", "")
            elif params["dbid"] and (int(params["dbid"]) > -1):
                MovieId = GetImdbIDFromDatabase("movie", params["dbid"])
                log("IMDBId from local DB:" + str(MovieId))
            else:
                MovieId = ""
            if MovieId:
                passListToSkin('SimilarMovies', GetSimilarMovies(MovieId), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'studio':
            passListToSkin('StudioInfo', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["studio"]:
                CompanyId = SearchforCompany(params["studio"])
                passListToSkin('StudioInfo', GetCompanyInfo(CompanyId), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'set':
            passListToSkin('MovieSetItems', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["dbid"] and not "show" in str(params["type"]):
                name = GetMovieSetName(params["dbid"])
                if name:
                    params["setid"] = SearchForSet(name)
            if params["setid"]:
                SetData, info = GetSetMovies(params["setid"])
                if SetData:
                    passListToSkin('MovieSetItems', SetData, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'movielists':
            passListToSkin('MovieLists', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["dbid"]:
                movieid = GetImdbIDFromDatabase("movie", params["dbid"])
                log("MovieDB Id:" + str(movieid))
                if movieid:
                    passListToSkin('MovieLists', GetMovieLists(movieid), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'keywords':
            passListToSkin('Keywords', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["dbid"]:
                movieid = GetImdbIDFromDatabase("movie", params["dbid"])
                log("MovieDB Id:" + str(movieid))
                if movieid:
                    passListToSkin('Keywords', GetMovieKeywords(movieid), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'popularpeople':
            passListToSkin('PopularPeople', GetPopularActorList(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'extendedinfo':
            from DialogVideoInfo import DialogVideoInfo
            if params.get("handle", ""):
                xbmcplugin.endOfDirectory(params.get("handle", ""))
            dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=params.get("id", ""), dbid=params["dbid"], imdbid=params.get("imdbid", ""), name=params.get("name", ""))
            dialog.doModal()
        elif info == 'extendedactorinfo':
                from DialogActorInfo import DialogActorInfo
                dialog = DialogActorInfo(u'script-%s-DialogInfo.xml' % addon_name, addon_path, id=params.get("id", ""), name=params.get("name", ""))
                dialog.doModal()

        elif info == 'extendedtvinfo':
            from DialogTVShowInfo import DialogTVShowInfo
            if params.get("handle", ""):
                xbmcplugin.endOfDirectory(params.get("handle", ""))
            dialog = DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=params.get("id", ""), dbid=params["dbid"], imdbid=params.get("imdbid", ""), name=params.get("name", ""))
            dialog.doModal()
        elif info == 'seasoninfo':
            passListToSkin("SeasonVideos", None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["tvshow"] and params["season"]:
                from DialogSeasonInfo import DialogSeasonInfo
                dialog = DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, tvshow=params["tvshow"], season=params["season"])
                dialog.doModal()
        elif info == 'directormovies':
            passListToSkin('DirectorMovies', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["director"]:
                directorid = GetPersonID(params["director"])
                if directorid:
                    passListToSkin('DirectorMovies', GetDirectorMovies(directorid), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'writermovies':
            passListToSkin('WriterMovies', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["writer"] and not params["writer"].split(" / ")[0] == params["director"].split(" / ")[0]:
                writerid = GetPersonID(params["writer"])
                if writerid:
                    passListToSkin('WriterMovies', GetDirectorMovies(writerid), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'similarmoviestrakt':
            passListToSkin('SimilarMovies', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if (params.get("id", "") or params["dbid"]):
                if params["dbid"]:
                    movieid = GetImdbIDFromDatabase("movie", params["dbid"])
                else:
                    movieid = params.get("id", "")
                passListToSkin('SimilarMovies', GetSimilarTrakt("movie", movieid), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'similartvshowstrakt':
            passListToSkin('SimilarTVShows', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if (params.get("id", "") or params["dbid"]):
                if params["dbid"]:
                    if params["type"] == "episode":
                        tvshowid = GetImdbIDFromDatabasefromEpisode(params["dbid"])
                    else:
                        tvshowid = GetImdbIDFromDatabase("tvshow", params["dbid"])
                else:
                    tvshowid = params.get("id", "")
                passListToSkin('SimilarTVShows', GetSimilarTrakt("show", tvshowid), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'airingshows':
            passListToSkin('AiringShows', GetTraktCalendarShows("shows"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'premiereshows':
            passListToSkin('PremiereShows', GetTraktCalendarShows("premieres"), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'trendingshows':
            passListToSkin('TrendingShows', GetTrendingShows(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'trendingmovies':
            passListToSkin('TrendingMovies', GetTrendingMovies(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'similarartistsinlibrary':
            passListToSkin('SimilarArtists', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["artist_mbid"]:
                passListToSkin('SimilarArtists', GetSimilarArtistsInLibrary(params["artist_mbid"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'artistevents':
            passListToSkin('ArtistEvents', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["artist_mbid"]:
                passListToSkin('ArtistEvents', GetEvents(params["artist_mbid"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'youtubesearch':
            homewindow.setProperty('%sSearchValue' % params.get("prefix", ""), params.get("id", ""))  # set properties
            passListToSkin('YoutubeSearch', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params.get("id", ""):
                passListToSkin('YoutubeSearch', GetYoutubeSearchVideosV3(params.get("id", ""), params["hd"], params["orderby"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'youtubeplaylist':
            passListToSkin('YoutubePlaylist', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params.get("id", ""):
                passListToSkin('YoutubePlaylist', GetYoutubePlaylistVideos(params.get("id", "")), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'youtubeusersearch':
            passListToSkin('YoutubeUserSearch', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params.get("id", ""):
                passListToSkin('YoutubeUserSearch', GetYoutubeUserVideos(params.get("id", "")), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'nearevents':
            passListToSkin('NearEvents', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('NearEvents', GetNearEvents(params["tag"], params["festivalsonly"], params["lat"], params["lon"], params["location"], params["distance"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'trackinfo':
            homewindow.setProperty('%sSummary' % params.get("prefix", ""), "")  # set properties
            if params["artistname"] and params["trackname"]:
                TrackInfo = GetTrackInfo(params["artistname"], params["trackname"])
                homewindow.setProperty('%sSummary' % params.get("prefix", ""), TrackInfo["summary"])  # set properties
        elif info == 'venueevents':
            passListToSkin('VenueEvents', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            if params["location"]:
                params["id"] = GetVenueID(params["location"])
            if params.get("id", ""):
                passListToSkin('VenueEvents', GetVenueEvents(params.get("id", "")), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            else:
                Notify("Error", "Could not find venue")
        elif info == 'topartistsnearevents':
            passListToSkin('TopArtistsNearEvents', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            artists = GetXBMCArtists()
            events = GetArtistNearEvents(artists["result"]["artists"][0:49])
            passListToSkin('TopArtistsNearEvents', events, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'channels':
            channels = create_channel_list()
      #      prettyprint(channels)
        elif info == 'favourites':
            if params.get("id", ""):
                favourites = GetFavouriteswithType(params.get("id", ""))
            else:
                favourites = GetFavourites()
                homewindow.setProperty('favourite.count', str(len(favourites)))
                if len(favourites) > 0:
                    homewindow.setProperty('favourite.1.name', favourites[-1]["Label"])
            passListToSkin('Favourites', favourites, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'json':
            passListToSkin('RSS', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            videos = GetYoutubeVideos(params["feed"], params.get("prefix", ""))
            passListToSkin('RSS', videos, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'similarlocal' and params["dbid"]:
            passListToSkin('SimilarLocalMovies', None, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
            passListToSkin('SimilarLocalMovies', GetSimilarFromOwnLibrary(params["dbid"]), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'iconpanel':
            passListToSkin('IconPanel', GetIconPanel(1), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'weather':
            passListToSkin('WeatherImages', GetWeatherImages(), params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'updatexbmcdatabasewithartistmbidbg':
            SetMusicBrainzIDsForAllArtists(False, False)
        elif info == 'setfocus':
            params["control"] = ""  # workaround to avoid breaking PlayMedia
            xbmc.executebuiltin("SetFocus(22222)")
        elif info == 'playliststats':
            GetPlaylistStats(params.get("id", ""))
        elif info == "sortletters":
            listitems = GetSortLetters(params["path"], params.get("id", ""))
            passListToSkin('SortLetters', listitems, params.get("prefix", ""), params.get("window", ""), params.get("handle", ""), params.get("limit", 20))
        elif info == 'slideshow':
            windowid = xbmcgui.getCurrentWindowId()
            Window = xbmcgui.Window(windowid)
            # focusid = Window.getFocusId()
            itemlist = Window.getFocus()
            numitems = itemlist.getSelectedPosition()
            log("items:" + str(numitems))
            for i in range(0, numitems):
                Notify(item.getProperty("Image"))
        elif info == 'action':
            xbmc.executebuiltin(params.get("id", ""))
        elif info == 'bounce':
            homewindow.setProperty(params.get("name", ""), "True")
            xbmc.sleep(200)
            homewindow.clearProperty(params.get("name", ""))
        elif info == "youtubevideo":
            if params.get("id", ""):
                params["control"] = ""  # workaround to avoid breaking PlayMedia
                PlayTrailer(params.get("id", ""))
        elif info == 'playtrailer':
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            xbmc.sleep(500)
            if params.get("id", ""):
                MovieId = params.get("id", "")
            elif params["dbid"] and (int(params["dbid"]) > -1):
                MovieId = GetImdbIDFromDatabase("movie", params["dbid"])
                log("MovieDBID from local DB:" + str(MovieId))
            elif params.get("imdbid", ""):
                MovieId = GetMovieDBID(params.get("imdbid", ""))
            else:
                MovieId = ""
            if MovieId:
                trailer = GetTrailer(MovieId)
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                if trailer:
                    PlayTrailer(trailer)
                    params["control"] = ""  # workaround to avoid breaking PlayMedia
                else:
                    Notify("Error", "No Trailer available")
        elif info == 'updatexbmcdatabasewithartistmbid':
            SetMusicBrainzIDsForAllArtists(True, False)
