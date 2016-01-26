# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import LastFM
import TheAudioDB as AudioDB
import TheMovieDB as tmdb
from Utils import *
from local_db import local_db
import YouTube
import Trakt
import RottenTomatoes
import KodiJson
from WindowManager import wm
from VideoPlayer import PLAYER


def start_info_actions(infos, params):
    if "artistname" in params:
        params["artistname"] = params.get("artistname", "").split(" feat. ")[0].strip()
        params["artist_mbid"] = fetch_musicbrainz_id(params["artistname"])
    prettyprint(params)
    prettyprint(infos)
    if "prefix" in params and (not params["prefix"].endswith('.')) and (params["prefix"]):
        params["prefix"] = params["prefix"] + '.'
    for info in infos:
        data = [], ""
        #  Images
        if info == 'xkcd':
            from MiscScraper import get_xkcd_images
            data = get_xkcd_images(), "XKCD"
        elif info == 'cyanide':
            from MiscScraper import get_cyanide_images
            data = get_cyanide_images(), "CyanideHappiness"
        elif info == 'dailybabes':
            from MiscScraper import get_babe_images
            data = get_babe_images(), "DailyBabes"
        elif info == 'dailybabe':
            from MiscScraper import get_babe_images
            data = get_babe_images(single=True), "DailyBabe"
        # Audio
        elif info == 'discography':
            discography = AudioDB.get_artist_discography(params["artistname"])
            if not discography:
                discography = LastFM.get_artist_albums(params.get("artist_mbid"))
            data = discography, "discography"
        elif info == 'mostlovedtracks':
            data = AudioDB.get_most_loved_tracks(params["artistname"]), "MostLovedTracks"
        elif info == 'musicvideos':
            pass
            # if "audiodbid" in artist_details:
            #     data = get_musicvideos(artist_details["audiodbid"]), "MusicVideos"
        elif info == 'trackdetails':
            if params.get("id", ""):
                data = AudioDB.get_track_details(params.get("id", "")), "Trackinfo"
        elif info == 'albumshouts':
            if params["artistname"] and params["albumname"]:
                data = LastFM.get_album_shouts(params["artistname"], params["albumname"]), "Shout"
        elif info == 'artistshouts':
            if params["artistname"]:
                data = LastFM.get_artist_shouts(params["artistname"]), "Shout"
        elif info == 'topartists':
            data = LastFM.get_top_artists(), "TopArtists"
        elif info == 'hypedartists':
            data = LastFM.get_hyped_artists(), "HypedArtists"
        elif info == 'latestdbmovies':
            data = local_db.get_movies('"sort": {"order": "descending", "method": "dateadded"}', params.get("limit", 10)), "LatestMovies"
        elif info == 'randomdbmovies':
            data = local_db.get_movies('"sort": {"method": "random"}', params.get("limit", 10)), "RandomMovies"
        elif info == 'inprogressdbmovies':
            method = '"sort": {"order": "descending", "method": "lastplayed"}, "filter": {"field": "inprogress", "operator": "true", "value": ""}'
            data = local_db.get_movies(method, params.get("limit", 10)), "RecommendedMovies"
    #  RottenTomatoesMovies
        elif info == 'intheaters':
            data = RottenTomatoes.get_movies("movies/in_theaters"), "InTheatersMovies"
        elif info == 'boxoffice':
            data = RottenTomatoes.get_movies("movies/box_office"), "BoxOffice"
        elif info == 'opening':
            data = RottenTomatoes.get_movies("movies/opening"), "Opening"
        elif info == 'comingsoon':
            data = RottenTomatoes.get_movies("movies/upcoming"), "ComingSoonMovies"
        elif info == 'toprentals':
            data = RottenTomatoes.get_movies("dvds/top_rentals"), "TopRentals"
        elif info == 'currentdvdreleases':
            data = RottenTomatoes.get_movies("dvds/current_releases"), "CurrentDVDs"
        elif info == 'newdvdreleases':
            data = RottenTomatoes.get_movies("dvds/new_releases"), "NewDVDs"
        elif info == 'upcomingdvds':
            data = RottenTomatoes.get_movies("dvds/upcoming"), "UpcomingDVDs"
        #  The MovieDB
        elif info == 'incinemas':
            data = tmdb.get_tmdb_movies("now_playing"), "InCinemasMovies"
        elif info == 'upcoming':
            data = tmdb.get_tmdb_movies("upcoming"), "UpcomingMovies"
        elif info == 'topratedmovies':
            data = tmdb.get_tmdb_movies("top_rated"), "TopRatedMovies"
        elif info == 'popularmovies':
            data = tmdb.get_tmdb_movies("popular"), "PopularMovies"
        elif info == 'ratedmovies':
            data = tmdb.get_rated_media_items("movies"), "RatedMovies"
        elif info == 'starredmovies':
            data = tmdb.get_fav_items("movies"), "StarredMovies"
        elif info == 'accountlists':
            account_lists = tmdb.handle_misc(tmdb.get_account_lists())
            for item in account_lists:
                item["directory"] = True
            data = account_lists, "AccountLists"
        elif info == 'listmovies':
            movies = tmdb.get_movies_from_list(params["id"])
            data = movies, "AccountLists"
        elif info == 'airingtodaytvshows':
            data = tmdb.get_tmdb_shows("airing_today"), "AiringTodayTVShows"
        elif info == 'onairtvshows':
            data = tmdb.get_tmdb_shows("on_the_air"), "OnAirTVShows"
        elif info == 'topratedtvshows':
            data = tmdb.get_tmdb_shows("top_rated"), "TopRatedTVShows"
        elif info == 'populartvshows':
            data = tmdb.get_tmdb_shows("popular"), "PopularTVShows"
        elif info == 'ratedtvshows':
            data = tmdb.get_rated_media_items("tv"), "RatedTVShows"
        elif info == 'starredtvshows':
            data = tmdb.get_fav_items("tv"), "StarredTVShows"
        elif info == 'similarmovies':
            movie_id = params.get("id", False)
            if not movie_id:
                movie_id = tmdb.get_movie_tmdb_id(imdb_id=params.get("imdb_id", False),
                                                  dbid=params.get("dbid", False))
            if movie_id:
                data = tmdb.get_similar_movies(movie_id), "SimilarMovies"
        elif info == 'similartvshows':
            tvshow_id = None
            dbid = params.get("dbid", False)
            name = params.get("name", False)
            tmdb_id = params.get("tmdb_id", False)
            tvdb_id = params.get("tvdb_id", False)
            imdb_id = params.get("imdb_id", False)
            if tmdb_id:
                tvshow_id = tmdb_id
            elif dbid and int(dbid) > 0:
                tvdb_id = local_db.get_imdb_id("tvshow", dbid)
                if tvdb_id:
                    tvshow_id = tmdb.get_show_tmdb_id(tvdb_id)
            elif tvdb_id:
                tvshow_id = tmdb.get_show_tmdb_id(tvdb_id)
            elif imdb_id:
                tvshow_id = tmdb.get_show_tmdb_id(imdb_id, "imdb_id")
            elif name:
                tvshow_id = tmdb.search_media(media_name=name,
                                              year="",
                                              media_type="tv")
            if tvshow_id:
                data = tmdb.get_similar_tvshows(tvshow_id), "SimilarTVShows"
        elif info == 'studio':
            if "id" in params and params["id"]:
                data = tmdb.get_company_data(params["id"]), "StudioInfo"
            elif "studio" in params and params["studio"]:
                company_data = tmdb.search_company(params["studio"])
                if company_data:
                    data = tmdb.get_company_data(company_data[0]["id"]), "StudioInfo"
        elif info == 'set':
            if params.get("dbid") and "show" not in str(params.get("type", "")):
                name = local_db.get_set_name(params["dbid"])
                if name:
                    params["setid"] = tmdb.get_set_id(name)
            if params.get("setid"):
                set_data, _ = tmdb.get_set_movies(params["setid"])
                if set_data:
                    data = set_data, "MovieSetItems"
        elif info == 'movielists':
            movie_id = params.get("id", False)
            if not movie_id:
                movie_id = tmdb.get_movie_tmdb_id(imdb_id=params.get("imdb_id", False),
                                                  dbid=params.get("dbid", False))
            if movie_id:
                data = tmdb.get_movie_lists(movie_id), "MovieLists"
        elif info == 'keywords':
            movie_id = params.get("id", False)
            if not movie_id:
                movie_id = tmdb.get_movie_tmdb_id(imdb_id=params.get("imdb_id", False),
                                                  dbid=params.get("dbid", False))
            if movie_id:
                data = tmdb.get_keywords(movie_id), "Keywords"
        elif info == 'popularpeople':
            data = tmdb.get_popular_actors(), "PopularPeople"
        elif info == 'directormovies':
            if params.get("director"):
                director_info = tmdb.get_person_info(person_label=params["director"],
                                                     skip_dialog=True)
                if director_info and director_info.get("id"):
                    movies = tmdb.get_person_movies(director_info["id"])
                    for item in movies:
                        del item["credit_id"]
                    data = merge_dict_lists(movies, key="department"), "DirectorMovies"
        elif info == 'writermovies':
            if params.get("writer") and not params["writer"].split(" / ")[0] == params.get("director", "").split(" / ")[0]:
                writer_info = tmdb.get_person_info(person_label=params["writer"],
                                                   skip_dialog=True)
                if writer_info and writer_info.get("id"):
                    movies = tmdb.get_person_movies(writer_info["id"])
                    for item in movies:
                        del item["credit_id"]
                    data = merge_dict_lists(movies, key="department"), "WriterMovies"
        elif info == 'similarmoviestrakt':
            if params.get("id", False) or params.get("dbid"):
                if params.get("dbid"):
                    movie_id = local_db.get_imdb_id("movie", params["dbid"])
                else:
                    movie_id = params.get("id", "")
                data = Trakt.get_similar("movie", movie_id), "SimilarMovies"
        elif info == 'similartvshowstrakt':
            if (params.get("id", "") or params["dbid"]):
                if params.get("dbid"):
                    if params.get("type") == "episode":
                        tvshow_id = local_db.get_tvshow_id_by_episode(params["dbid"])
                    else:
                        tvshow_id = local_db.get_imdb_id(media_type="tvshow",
                                                         dbid=params["dbid"])
                else:
                    tvshow_id = params.get("id", "")
                data = Trakt.get_similar("show", tvshow_id), "SimilarTVShows"
        elif info == 'airingshows':
            data = Trakt.get_calendar_shows("shows"), "AiringShows"
        elif info == 'premiereshows':
            data = Trakt.get_calendar_shows("premieres"), "PremiereShows"
        elif info == 'trendingshows':
            data = Trakt.get_trending_shows(), "TrendingShows"
        elif info == 'trendingmovies':
            data = Trakt.get_trending_movies(), "TrendingMovies"
        elif info == 'similarartistsinlibrary':
            if params.get("artist_mbid"):
                data = local_db.get_similar_artists(params.get("artist_mbid")), "SimilarArtists"
        elif info == 'artistevents':
            if params.get("artist_mbid"):
                data = LastFM.get_events(params.get("artist_mbid")), "ArtistEvents"
        elif info == 'youtubesearch':
            HOME.setProperty('%sSearchValue' % params.get("prefix", ""), params.get("id", ""))  # set properties
            if params.get("id"):
                listitems = YouTube.search(search_str=params.get("id", ""),
                                           hd=params.get("hd", ""),
                                           orderby=params.get("orderby", "relevance"))
                data = listitems.get("listitems", []), "YoutubeSearch"
        elif info == 'youtubeplaylist':
            if params.get("id"):
                data = YouTube.get_playlist_videos(params.get("id", "")), "YoutubePlaylist"
        elif info == 'youtubeusersearch':
            user_name = params.get("id", "")
            if user_name:
                playlists = YouTube.get_user_playlists(user_name)
                data = YouTube.get_playlist_videos(playlists["uploads"]), "YoutubeUserSearch"
        elif info == 'nearevents':
            eventinfo = LastFM.get_near_events(tag=params.get("tag", ""),
                                               festivals_only=params.get("festivalsonly", ""),
                                               lat=params.get("lat", ""),
                                               lon=params.get("lon", ""),
                                               location=params.get("location", ""),
                                               distance=params.get("distance", ""))
            data = eventinfo, "NearEvents"
        elif info == 'trackinfo':
            HOME.setProperty('%sSummary' % params.get("prefix", ""), "")  # set properties
            if params["artistname"] and params["trackname"]:
                track_info = LastFM.get_track_info(artist=params["artistname"],
                                                   track=params["trackname"])
                HOME.setProperty('%sSummary' % params.get("prefix", ""), track_info["summary"])  # set properties
        elif info == 'venueevents':
            if params["location"]:
                params["id"] = LastFM.get_venue_id(params["location"])
            if params.get("id", ""):
                data = LastFM.get_venue_events(params.get("id", "")), "VenueEvents"
            else:
                notify("Error", "Could not find venue")
        elif info == 'topartistsnearevents':
            artists = local_db.get_artists()
            import BandsInTown
            data = BandsInTown.get_near_events(artists[0:49]), "TopArtistsNearEvents"
        elif info == 'favourites':
            if params.get("id", ""):
                favs = get_favs_by_type(params.get("id", ""))
            else:
                favs = get_favs()
                HOME.setProperty('favourite.count', str(len(favs)))
                if favs:
                    HOME.setProperty('favourite.1.name', favs[-1]["Label"])
            data = favs, "Favourites"
        elif info == 'similarlocal' and "dbid" in params:
            data = local_db.get_similar_movies(params["dbid"]), "SimilarLocalMovies"
        elif info == 'iconpanel':
            data = get_icon_panel(int(params["id"])), "IconPanel" + str(params["id"])
        elif info == 'autocomplete':
            data = get_autocomplete_items(params["id"]), "AutoComplete"
        elif info == 'weather':
            data = get_weather_images(), "WeatherImages"
        elif info == "sortletters":
            data = get_sort_letters(params["path"], params.get("id", "")), "SortLetters"

        # ACTIONS
        elif info == 't9input':
            resolve_url(params.get("handle"))
            from T9Search import T9Search
            dialog = T9Search(call=None,
                              start_value="")
            KodiJson.send_text(text=dialog.search_str)
        elif info in ['playmovie', 'playepisode', 'playmusicvideo', 'playalbum', 'playsong']:
            resolve_url(params.get("handle"))
            KodiJson.play_media(media_type=info.replace("play", ""),
                                dbid=params.get("dbid"),
                                resume=params.get("resume", "true"))
        elif info == "openinfodialog":
            resolve_url(params.get("handle"))
            dbid = xbmc.getInfoLabel("ListItem.DBID")
            if not dbid:
                dbid = xbmc.getInfoLabel("ListItem.Property(dbid)")
            if xbmc.getCondVisibility("Container.Content(movies)"):
                params = {"dbid": dbid,
                          "id": xbmc.getInfoLabel("ListItem.Property(id)"),
                          "name": xbmc.getInfoLabel("ListItem.Title")}
                start_info_actions(["extendedinfo"], params)
            elif xbmc.getCondVisibility("Container.Content(tvshows)"):
                params = {"dbid": dbid,
                          "id": xbmc.getInfoLabel("ListItem.Property(id)"),
                          "name": xbmc.getInfoLabel("ListItem.Title")}
                start_info_actions(["extendedtvinfo"], params)
            elif xbmc.getCondVisibility("Container.Content(seasons)"):
                params = {"tvshow": xbmc.getInfoLabel("ListItem.TVShowTitle"),
                          "season": xbmc.getInfoLabel("ListItem.Season")}
                start_info_actions(["seasoninfo"], params)
            elif xbmc.getCondVisibility("Container.Content(episodes)"):
                params = {"tvshow": xbmc.getInfoLabel("ListItem.TVShowTitle"),
                          "season": xbmc.getInfoLabel("ListItem.Season"),
                          "episode": xbmc.getInfoLabel("ListItem.Episode")}
                start_info_actions(["extendedepisodeinfo"], params)
            elif xbmc.getCondVisibility("Container.Content(actors) | Container.Content(directors)"):
                params = {"name": xbmc.getInfoLabel("ListItem.Label")}
                start_info_actions(["extendedactorinfo"], params)
            else:
                notify("Error", "Could not find valid content type")
        elif info == "ratedialog":
            resolve_url(params.get("handle"))
            if xbmc.getCondVisibility("Container.Content(movies)"):
                params = {"dbid": xbmc.getInfoLabel("ListItem.DBID"),
                          "id": xbmc.getInfoLabel("ListItem.Property(id)"),
                          "type": "movie"}
                start_info_actions(["ratemedia"], params)
            elif xbmc.getCondVisibility("Container.Content(tvshows)"):
                params = {"dbid": xbmc.getInfoLabel("ListItem.DBID"),
                          "id": xbmc.getInfoLabel("ListItem.Property(id)"),
                          "type": "tv"}
                start_info_actions(["ratemedia"], params)
            elif xbmc.getCondVisibility("Container.Content(episodes)"):
                params = {"tvshow": xbmc.getInfoLabel("ListItem.TVShowTitle"),
                          "season": xbmc.getInfoLabel("ListItem.Season"),
                          "type": "episode"}
                start_info_actions(["ratemedia"], params)
        elif info == 'youtubebrowser':
            resolve_url(params.get("handle"))
            wm.open_youtube_list(search_str=params.get("id", ""))
        elif info == 'moviedbbrowser':
            resolve_url(params.get("handle"))
            search_str = params.get("id", "")
            if not search_str and params.get("search", ""):
                result = xbmcgui.Dialog().input(heading=LANG(16017),
                                                type=xbmcgui.INPUT_ALPHANUM)
                if result and result > -1:
                    search_str = result
                else:
                    return None
            wm.open_video_list(search_str=search_str,
                               mode="search")
        elif info == 'extendedinfo':
            resolve_url(params.get("handle"))
            HOME.setProperty('infodialogs.active', "true")
            wm.open_movie_info(movie_id=params.get("id", ""),
                               dbid=params.get("dbid", None),
                               imdb_id=params.get("imdb_id", ""),
                               name=params.get("name", ""))
            HOME.clearProperty('infodialogs.active')
        elif info == 'extendedactorinfo':
            resolve_url(params.get("handle"))
            HOME.setProperty('infodialogs.active', "true")
            wm.open_actor_info(actor_id=params.get("id", ""),
                               name=params.get("name", ""))
            HOME.clearProperty('infodialogs.active')
        elif info == 'extendedtvinfo':
            resolve_url(params.get("handle"))
            HOME.setProperty('infodialogs.active', "true")
            wm.open_tvshow_info(tvshow_id=params.get("id", ""),
                                tvdb_id=params.get("tvdb_id", ""),
                                dbid=params.get("dbid", None),
                                imdb_id=params.get("imdb_id", ""),
                                name=params.get("name", ""))
            HOME.clearProperty('infodialogs.active')
        elif info == 'seasoninfo':
            resolve_url(params.get("handle"))
            HOME.setProperty('infodialogs.active', "true")
            wm.open_season_info(tvshow=params.get("tvshow"),
                                dbid=params.get("dbid"),
                                season=params.get("season"))
            HOME.clearProperty('infodialogs.active')
        elif info == 'extendedepisodeinfo':
            resolve_url(params.get("handle"))
            HOME.setProperty('infodialogs.active', "true")
            wm.open_episode_info(tvshow=params.get("tvshow"),
                                 tvshow_id=params.get("tvshow_id"),
                                 dbid=params.get("dbid"),
                                 episode=params.get("episode"),
                                 season=params.get("season"))
            HOME.clearProperty('infodialogs.active')
        elif info == 'albuminfo':
            resolve_url(params.get("handle"))
            if params.get("id", ""):
                album_details = AudioDB.get_album_details(params.get("id", ""))
                pass_dict_to_skin(album_details, params.get("prefix", ""))
        elif info == 'artistdetails':
            resolve_url(params.get("handle"))
            artist_details = AudioDB.get_artist_details(params["artistname"])
            pass_dict_to_skin(artist_details, params.get("prefix", ""))
        elif info == 'ratemedia':
            resolve_url(params.get("handle"))
            media_type = params.get("type", False)
            if media_type:
                if params.get("id") and params["id"]:
                    tmdb_id = params["id"]
                elif media_type == "movie":
                    tmdb_id = tmdb.get_movie_tmdb_id(imdb_id=params.get("imdb_id", ""),
                                                     dbid=params.get("dbid", ""),
                                                     name=params.get("name", ""))
                elif media_type == "tv" and params["dbid"]:
                    tvdb_id = local_db.get_imdb_id(media_type="tvshow",
                                                   dbid=params["dbid"])
                    tmdb_id = tmdb.get_show_tmdb_id(tvdb_id=tvdb_id)
                else:
                    return False
                tmdb.set_rating_prompt(media_type=media_type,
                                       media_id=tmdb_id)
        elif info == 'setfocus':
            resolve_url(params.get("handle"))
            xbmc.executebuiltin("SetFocus(22222)")
        elif info == 'playliststats':
            resolve_url(params.get("handle"))
            get_playlist_stats(params.get("id", ""))
        elif info == 'slideshow':
            resolve_url(params.get("handle"))
            window_id = xbmcgui.getCurrentwindow_id()
            window = xbmcgui.Window(window_id)
            # focusid = Window.getFocusId()
            num_items = window.getFocus().getSelectedPosition()
            for i in range(0, num_items):
                notify(item.getProperty("Image"))
        elif info == 'action':
            resolve_url(params.get("handle"))
            for builtin in params.get("id", "").split("$$"):
                xbmc.executebuiltin(builtin)
            return None
        elif info == 'selectautocomplete':
            resolve_url(params.get("handle"))
            try:
                window_id = xbmcgui.getCurrentWindowDialogId()
                window = xbmcgui.Window(window_id)
            except:
                return None
            KodiJson.send_text(text=params.get("id"),
                               close_keyboard=False)
            # xbmc.executebuiltin("SendClick(103,32)")
            window.setFocusId(300)
        elif info == 'bounce':
            resolve_url(params.get("handle"))
            HOME.setProperty(params.get("name", ""), "True")
            xbmc.sleep(200)
            HOME.clearProperty(params.get("name", ""))
        elif info == "youtubevideo":
            resolve_url(params.get("handle"))
            xbmc.executebuiltin("Dialog.Close(all,true)")
            PLAYER.play_youtube_video(params.get("id", ""))
        elif info == 'playtrailer':
            resolve_url(params.get("handle"))
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            if params.get("id", ""):
                movie_id = params.get("id", "")
            elif int(params.get("dbid", -1)) > 0:
                movie_id = local_db.get_imdb_id(media_type="movie",
                                                dbid=params["dbid"])
            elif params.get("imdb_id", ""):
                movie_id = get_movie_tmdb_id(params.get("imdb_id", ""))
            else:
                movie_id = ""
            if movie_id:
                trailer = tmdb.get_trailer(movie_id)
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                xbmc.sleep(100)
                if trailer:
                    PLAYER.play_youtube_video(trailer)
                elif params.get("title"):
                    wm.open_youtube_list(search_str=params.get("title", ""))
                else:
                    xbmc.executebuiltin("Dialog.Close(busydialog)")
        elif info == 'deletecache':
            resolve_url(params.get("handle"))
            HOME.clearProperties()
            import shutil
            for rel_path in os.listdir(ADDON_DATA_PATH):
                path = os.path.join(ADDON_DATA_PATH, rel_path)
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                except Exception as e:
                    log(e)
            notify("Cache deleted")
        elif info == 'syncwatchlist':
            pass
        elif info == "widgetdialog":
            resolve_url(params.get("handle"))
            widget_selectdialog()
        listitems, prefix = data
        if params.get("handle"):
            xbmcplugin.addSortMethod(params.get("handle"), xbmcplugin.SORT_METHOD_TITLE)
            xbmcplugin.addSortMethod(params.get("handle"), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
            xbmcplugin.addSortMethod(params.get("handle"), xbmcplugin.SORT_METHOD_DURATION)
            if info.endswith("shows"):
                xbmcplugin.setContent(params.get("handle"), 'tvshows')
            else:
                xbmcplugin.setContent(params.get("handle"), 'movies')
        pass_list_to_skin(name=prefix,
                          data=listitems,
                          prefix=params.get("prefix", ""),
                          handle=params.get("handle", ""),
                          limit=params.get("limit", 20))


def resolve_url(handle):
    if handle:
        xbmcplugin.setResolvedUrl(handle=int(handle),
                                  succeeded=False,
                                  listitem=xbmcgui.ListItem())


