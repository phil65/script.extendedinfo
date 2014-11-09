List of possible ExtendedInfo script calls.
All calls can also be done by using a plugin path.

Example:
<content>plugin://script.extendedinfo?info=discography&amp;&amp;artistname=INSERT_ARTIST_NAME_HERE</content>
- keep Attention to the parameter separators ("&amp;&amp;")


#########################################################################################
Rotten Tomatoes
#########################################################################################

Run:
RunScript(script.extendedinfo,info=intheaters)          --> InTheatersMovies.%d.xxx
RunScript(script.extendedinfo,info=comingsoon)          --> ComingSoonMovies.%d.xxx
RunScript(script.extendedinfo,info=opening)             --> Opening.%d.xxx
RunScript(script.extendedinfo,info=boxoffice)           --> BoxOffice.%d.xxx
RunScript(script.extendedinfo,info=toprentals)          --> TopRentals.%d.xxx
RunScript(script.extendedinfo,info=currentdvdreleases)  --> CurrentDVDs.%d.xxx
RunScript(script.extendedinfo,info=newdvdreleases)      --> NewDVDs.%d.xxx
RunScript(script.extendedinfo,info=upcomingdvds)        --> UpcomingDVDs.%d.xxx

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
RunScript(script.extendedinfo,info=similarmovies)       --> SimilarMovies.%d
RunScript(script.extendedinfo,info=set)                 --> MovieSetItems.%d
-- required additional parameters: dbid=
RunScript(script.extendedinfo,info=directormovies)      --> DirectorMovies.%d
-- required additional parameters: director=
RunScript(script.extendedinfo,info=writermovies)        --> WriterMovies.%d
-- required additional parameters: writer=
RunScript(script.extendedinfo,info=studio)              --> StudioInfo.%d
-- required additional parameters: studio=


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


Run:

RunScript(script.extendedinfo,info=populartvshows)      --> PopularTVShows.%d
RunScript(script.extendedinfo,info=topratedtvshows)     --> TopRatedTVShows.%d
RunScript(script.extendedinfo,info=onairtvshows)        --> OnAirTVShows.%d
RunScript(script.extendedinfo,info=airingtodaytvshows)  --> AiringTodayTVShows.%d

Available Properties:

'Title':            TVShow Title
'ID':               TVShow MovieDB ID
'OriginalTitle':    TVShow OriginalTitle
'Rating':           TVShow Rating
'Votes':            Number of Votes for Rating
'Premiered':        TV Show First Air Date
'Art(poster)':      TVShow Poster
'Art(fanart)':      TVShow Fanart


#########################################################################################
Trakt.tv
#########################################################################################

Run:
RunScript(script.extendedinfo,info=trendingmovies)  --> TrendingMovies.%d

'Title'
'Plot'
'Tagline'
'Genre'
'Rating'
'mpaa'
'Year'
'Premiered'
'Runtime'
'Trailer'
'Art(poster)'
'Art(fanart)'


Run:

RunScript(script.extendedinfo,info=trendingshows)           --> TrendingShows.%d
RunScript(script.extendedinfo,info=similartvshowstrakt)     --> SimilarTVShows.%d
-- required additional parameters: dbid=

'TVShowTitle':      TVShow Title
'Duration':         Duration (?)
'Plot':             Plot
'ID':               ID
'Genre':            Genre
'Rating':           Rating
'mpaa':             mpaa
'Year':             Release Year
'Premiered':        First Air Date
'Status':           TVShow Status
'Studio':           TVShow Studio
'Country':          Production Country
'Votes':            Amount of Votes
'Watchers':         Amount of Watchers
'AirDay':           Day episode is aired
'AirShortTime':     Time episode is aired
'Art(poster)':      TVShow Poster
'Art(banner)':      TVShow Banner
'Art(fanart)':      TVShow Fanart


RunScript(script.extendedinfo,info=airingshows)         --> AiringShows.%d
RunScript(script.extendedinfo,info=premiereshows)       --> PremiereShows.%d

'Title':         Episode Title
'TVShowTitle':   TVShow Title
'Plot':          Episode Plot
'Genre':         TVShow Genre
'Runtime':       Episode Duration
'Year':          Episode Release Year
'Certification': TVShow Mpaa Rating
'Studio':        TVShow Studio
'Thumb':         Episode Thumb
'Art(poster)':   TVShow Poster
'Art(banner)':   TVShow Banner
'Art(fanart)':   TVShow Fanart


#########################################################################################
TheAudioDB
#########################################################################################

RunScript(script.extendedinfo,info=discography)         --> Discography.%d
-- required additional parameters: artistname=

'Label':           Album Title
'artist':          Album Artist
'mbid':            Album MBID
'id':              Album AudioDB ID
'Description':     Album Description
'Genre':           Album Genre
'Mood':            Album Mood
'Speed':           Album Speed
'Theme':           Album Theme
'Type':            Album Type
'thumb':           Album Thumb
'year':            Album Release Year
'Sales':           Album Sales


RunScript(script.extendedinfo,info=mostlovedtracks)         --> MostLovedTracks.%d
-- required additional parameters: artistname=
RunScript(script.extendedinfo,info=albuminfo)               --> TrackInfo.%d
-- required additional parameters: id= ???

'Label':       Track Name
'Artist':      Artist Name
'mbid':        Track MBID
'Album':       Album Title
'Thumb':       Album Thumb
'Path':        Link to Youtube Video


RunScript(script.extendedinfo,info=artistdetails) ???



#########################################################################################
LastFM
#########################################################################################

RunScript(script.extendedinfo,info=albumshouts)
-- required additional parameters: artistname=, albumname=
RunScript(script.extendedinfo,info=artistshouts)
-- required additional parameters: artistname=

'comment':  Tweet Content
'author':   Tweet Author
'date':     Tweet Date


RunScript(script.extendedinfo,info=topartists)
RunScript(script.extendedinfo,info=hypedartists)


'Title':        Artist Name
'mbid':         Artist MBID
'Thumb':        Artist Thumb
'Listeners':    actual Listeners


RunScript(script.extendedinfo,info=nearevents)       --> NearEvents.%d
-- optional parameters: lat=, lon=, location=, distance=, festivalsonly=, tag=

'date':         Event Date
'name':         Venue Name
'venue_id':     Venue ID
'event_id':     Event ID
'street':       Venue Street
'eventname':    Event Title
'website':      Event Website
'description':  Event description
'postalcode':   Venue PostalCode
'city':         Venue city
'country':      Venue country
'lat':          Venue latitude
'lon':          Venue longitude
'artists':      Event artists
'headliner':    Event Headliner
'googlemap':    GoogleMap of venue location
'artist_image': Artist image
'venue_image':  Venue image


#########################################################################################
YouTube
#########################################################################################

RunScript(script.extendedinfo,info=youtubesearch)           --> YoutubeSearch.%d
-- required additional parameters: id=
RunScript(script.extendedinfo,info=youtubeplaylist)         --> YoutubePlaylist.%d
-- required additional parameters: id=
RunScript(script.extendedinfo,info=youtubeusersearch)       --> YoutubeUserSearch.%d
-- required additional parameters: id=

'Thumb':        Video Thumbnail
'Description':  Video Description
'Title':        Video Title
'Date':         Video Upload Date


#########################################################################################
Misc Images
#########################################################################################

RunScript(script.extendedinfo,info=xkcd)          --> XKCD.%d
RunScript(script.extendedinfo,info=cyanide)       --> CyanideHappiness.%d
RunScript(script.extendedinfo,info=dailybabe)     --> DailyBabe.%d
RunScript(script.extendedinfo,info=dailybabes)    --> DailyBabes.%d

'Thumb':        Image
'Title':        Image Title
'Description':  Image Description (only XKCD)

