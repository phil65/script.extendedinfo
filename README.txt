#########################################################################################
Rotten Tomatoes
#########################################################################################

Run:
RunScript(script.extendedinfo,info=intheaters)          --> InTheatersMovies.%d.xxx
RunScript(script.extendedinfo,info=comingsoon)          --> ComingSoonMovies.%d.xxx
RunScript(script.extendedinfo,info=opening)             --> Opening.%d.xxx
RunScript(script.extendedinfo,info=boxoffice)           --> BoxOffice.%d.xxx
RunScript(script.extendedinfo,info=toprentals)          --> TopRentals.%d.xxx
RunScript(script.extendedinfo,info=currentdvdreleases)  --> TopRentals.%d.xxx
RunScript(script.extendedinfo,info=newdvdreleases)      --> TopRentals.%d.xxx
RunScript(script.extendedinfo,info=upcomingdvds)        --> TopRentals.%d.xxx

Available Properties:

'Title':        Movie Title
'Art(poster)':  Movie Poster
'imdbid':       IMDB ID
'Duration':     Movie Duration
'Year':         Release Year
'Premiered':    Release Date
'mpaa':         MPAA Rating
'Rating':       Audience Rating (0-10)
'Plot':         Movie Plot


#########################################################################################
The MovieDB
#########################################################################################

Run:
RunScript(script.extendedinfo,info=incinemas)           --> InCinemasMovies.%d
RunScript(script.extendedinfo,info=upcoming)            --> UpcomingMovies.%d
RunScript(script.extendedinfo,info=popularmovies)       --> PopularMovies.%d
RunScript(script.extendedinfo,info=topratedmovies)      --> TopRatedMovies.%d
RunScript(script.extendedinfo,info=populartvshows)
RunScript(script.extendedinfo,info=topratedtvshows)
RunScript(script.extendedinfo,info=onairtvshows)
RunScript(script.extendedinfo,info=airingtodaytvshows)

Available Properties:

'Art(fanart)':      Movie Fanart
'Art(poster)':      Movie Poster
'Title':            Movie Title
'OriginalTitle':    Movie OriginalTitle
'ID':               TheMovieDB ID
'Rating':           Movie Rating (0-10)
'Votes':            Vote Count for Rating
'Year':             Release Year
'Premiered':        Release Date


Available labels for TVShows:
info=populartvshows         --> PopularTVShows.%d
info=topratedtvshows        --> TopRatedTVShows.%d
info=onairtvshows           --> OnAirTVShows.%d
info=airingtodaytvshows     --> AiringTodayTVShows.%d

$INFO[Window(Home).Property(PopularTVShows.%d.Title)]
$INFO[Window(Home).Property(PopularTVShows.%d.OriginalTitle)]
$INFO[Window(Home).Property(PopularTVShows.%d.Rating)]
$INFO[Window(Home).Property(PopularTVShows.%d.Premiered)]
$INFO[Window(Home).Property(PopularTVShows.%d.Art(poster))]
$INFO[Window(Home).Property(PopularTVShows.%d.Art(fanart))]


#########################################################################################
Trakt.tv
#########################################################################################

Run:
RunScript(script.extendedinfo,info=trendingmovies)
RunScript(script.extendedinfo,info=trendingshows)
RunScript(script.extendedinfo,info=airingshows)

Available labels for Trending Movies:
info=trendingmovies --> TrendingMovies.%d

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
info=trendingshows  --> TrendingShows.%d

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
info=airingshows        --> AiringShows.%d

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
