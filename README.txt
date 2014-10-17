#########################################################################################

Rotten Tomatoes

Run:
RunScript(script.extendedinfo,info=intheaters)
RunScript(script.extendedinfo,info=comingsoon)
RunScript(script.extendedinfo,info=opening)
RunScript(script.extendedinfo,info=boxoffice)

Available labels:
info=intheaters --> InTheatersMovies.%d
info=comingsoon --> ComingSoonMovies.%d
info=opening 		--> Opening.%d
info=boxoffice 	--> BoxOffice.%d

$INFO[Window(Home).Property(InTheatersMovies.%d.Title)]
$INFO[Window(Home).Property(InTheatersMovies.%d.Plot)]
$INFO[Window(Home).Property(InTheatersMovies.%d.Rating)]
$INFO[Window(Home).Property(InTheatersMovies.%d.mpaa)]
$INFO[Window(Home).Property(InTheatersMovies.%d.Year)]
$INFO[Window(Home).Property(InTheatersMovies.%d.Premiered)]
$INFO[Window(Home).Property(InTheatersMovies.%d.Runtime)]
$INFO[Window(Home).Property(InTheatersMovies.%d.Art(poster))]


#########################################################################################
#########################################################################################


The MovieDB

Run:
RunScript(script.extendedinfo,info=incinemas)
RunScript(script.extendedinfo,info=upcoming)
RunScript(script.extendedinfo,info=popularmovies)
RunScript(script.extendedinfo,info=topratedmovies)
RunScript(script.extendedinfo,info=populartvshows)
RunScript(script.extendedinfo,info=topratedtvshows)
RunScript(script.extendedinfo,info=onairtvshows)
RunScript(script.extendedinfo,info=airingtodaytvshows)


Available labels for Movies:
info=incinemas					--> InCinemasMovies.%d
info=upcoming						--> UpcomingMovies.%d
info=popularmovies			--> PopularMovies.%d
info=topratedmovies			--> TopRatedMovies.%d

$INFO[Window(Home).Property(InCinemasMovies.%d.Title)]
$INFO[Window(Home).Property(InCinemasMovies.%d.OriginalTitle)]
$INFO[Window(Home).Property(InCinemasMovies.%d.Rating)]
$INFO[Window(Home).Property(InCinemasMovies.%d.Year)]
$INFO[Window(Home).Property(InCinemasMovies.%d.Premiered)]
$INFO[Window(Home).Property(InCinemasMovies.%d.Art(poster))]
$INFO[Window(Home).Property(InTheatersMovies.%d.Art(fanart))]


Available labels for TVShows:
info=populartvshows			--> PopularTVShows.%d
info=topratedtvshows		--> TopRatedTVShows.%d
info=onairtvshows 			--> OnAirTVShows.%d
info=airingtodaytvshows --> AiringTodayTVShows.%d

$INFO[Window(Home).Property(PopularTVShows.%d.Title)]
$INFO[Window(Home).Property(PopularTVShows.%d.OriginalTitle)]
$INFO[Window(Home).Property(PopularTVShows.%d.Rating)]
$INFO[Window(Home).Property(PopularTVShows.%d.Premiered)]
$INFO[Window(Home).Property(PopularTVShows.%d.Art(poster))]
$INFO[Window(Home).Property(PopularTVShows.%d.Art(fanart))]


#########################################################################################
#########################################################################################


Trakt.tv

Run:
RunScript(script.extendedinfo,info=trendingmovies)
RunScript(script.extendedinfo,info=trendingshows)
RunScript(script.extendedinfo,info=airingshows)

Available labels for Trending Movies:
info=trendingmovies	--> TrendingMovies.%d

$INFO[Window(Home).Property(TrendingMovies.%d.Title)]
$INFO[Window(Home).Property(TrendingMovies.%d.Plot)]
$INFO[Window(Home).Property(TrendingMovies.%d.Tagline)]
$INFO[Window(Home).Property(TrendingMovies.%d.Genre)]
$INFO[Window(Home).Property(TrendingMovies.%d.Rating)]
$INFO[Window(Home).Property(TrendingMovies.%d.mpaa)]
$INFO[Window(Home).Property(TrendingMovies.%d.Year)]
$INFO[Window(Home).Property(TrendingMovies.%d.Premiered)]
$INFO[Window(Home).Property(TrendingMovies.%d.Runtime)]
$INFO[Window(Home).Property(TrendingMovies.%d.Trailer)]
$INFO[Window(Home).Property(TrendingMovies.%d.Art(poster))]
$INFO[Window(Home).Property(TrendingMovies.%d.Art(fanart))]



Available labels for Trending TVShows:
info=trendingshows	--> TrendingShows.%d

$INFO[Window(Home).Property(TrendingShows.%d.Title)]
$INFO[Window(Home).Property(TrendingShows.%d.Plot)]
$INFO[Window(Home).Property(TrendingShows.%d.Genre)]
$INFO[Window(Home).Property(TrendingShows.%d.Runtime)]
$INFO[Window(Home).Property(TrendingShows.%d.Rating)]
$INFO[Window(Home).Property(TrendingShows.%d.mpaa)]
$INFO[Window(Home).Property(TrendingShows.%d.Year)]
$INFO[Window(Home).Property(TrendingShows.%d.Premiered)]
$INFO[Window(Home).Property(TrendingShows.%d.Studio)]
$INFO[Window(Home).Property(TrendingShows.%d.Country)]
$INFO[Window(Home).Property(TrendingShows.%d.AirDay)]
$INFO[Window(Home).Property(TrendingShows.%d.AirShortTime)]
$INFO[Window(Home).Property(TrendingShows.%d.Label2)] -------> (AirDay & AirShortTime)
$INFO[Window(Home).Property(TrendingShows.%d.Art(poster))]
$INFO[Window(Home).Property(TrendingShows.%d.Art(banner))]
$INFO[Window(Home).Property(TrendingShows.%d.Art(fanart))]


Available labels for Airing TVShows:
info=airingshows		--> AiringShows.%d

$INFO[Window(Home).Property(AiringShows.%d.Title)] ----------> (Episode Title)
$INFO[Window(Home).Property(AiringShows.%d.TVShowTitle)]
$INFO[Window(Home).Property(AiringShows.%d.Plot)] -----------> (TVShow Plot)
$INFO[Window(Home).Property(AiringShows.%d.Genre)]
$INFO[Window(Home).Property(AiringShows.%d.Runtime)]
$INFO[Window(Home).Property(AiringShows.%d.Year)] -----------> (TVShow Year)
$INFO[Window(Home).Property(AiringShows.%d.Certification)] --> (TVShow MPAA)
$INFO[Window(Home).Property(AiringShows.%d.Studio)]
$INFO[Window(Home).Property(AiringShows.%d.Thumb)] ----------> (Episode Thumb)
$INFO[Window(Home).Property(AiringShows.%d.Art(poster))] ----> (TVShow Poster)
$INFO[Window(Home).Property(AiringShows.%d.Art(banner))] ----> (TVShow Banner)
$INFO[Window(Home).Property(AiringShows.%d.Art(fanart))] ----> (TVShow Fanart)


#########################################################################################
