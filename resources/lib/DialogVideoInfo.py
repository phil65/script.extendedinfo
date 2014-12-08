import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogVideoList
homewindow = xbmcgui.Window(10000)

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")


class DialogVideoInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        xbmcgui.WindowXMLDialog.__init__(self)
        tmdb_id = kwargs.get('id')
        dbid = kwargs.get('dbid')
        imdb_id = kwargs.get('imdbid')
        if __addon__.getSetting("tmdb_username"):
            get_session_id()
        if tmdb_id:
            self.MovieId = tmdb_id
        elif dbid and (int(dbid) > -1):
            self.MovieId = GetImdbIDFromDatabase("movie", dbid)
            log("IMDBId from local DB:" + str(self.MovieId))
        elif imdb_id:
            self.MovieId = GetMovieDBID(imdb_id)
        elif self.name:
            self.MovieId = search_movie(kwargs.get('name'))
        else:
            self.MovieId = ""
        if self.MovieId:
            self.movie, actors, similar_movies, lists, production_companies, releases, crew, genres, keywords, reviews = GetExtendedMovieInfo(self.MovieId, dbid)
            if not self.movie:
                self.close()
            xbmc.executebuiltin("RunScript(script.toolbox,info=blur,id=%s,radius=25,prefix=movie)" % self.movie["Thumb"])
            self.youtube_vids = GetYoutubeSearchVideosV3(self.movie["Label"] + " " + self.movie["Year"] + ", movie", "", "relevance", 15)
            self.set_listitems = []
            self.youtube_listitems = CreateListItems(self.youtube_vids, 0)
            if self.movie["SetId"]:
                self.set_listitems = CreateListItems(GetSetMovies(self.movie["SetId"]))
            # json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "videodb://movies/actors/", "media": "files"}, "id": 1}')
            # json_query = unicode(json_query, 'utf-8', errors='ignore')
            # json_response = simplejson.loads(json_query)
            # for db_actor in json_response["result"]["files"]:
            #     for movie_actor in actors:
            #         if db_actor["label"] == movie_actor["name"]:
            #             movie_actor.update({"dbid": db_actor["id"]})
            #             json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "videodb://movies/actors/%i/", "media": "files"}, "id": 1}' % db_actor["id"])
            #             json_query2 = unicode(json_query2, 'utf-8', errors='ignore')
            #             json_response2 = simplejson.loads(json_query2)
            #             numfiles = len(json_response2["result"]["files"])
            #             movie_actor.update({"moviecount": numfiles})
            passHomeDataToSkin(self.movie, "movie.", False, True)
         #   homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
        else:
            Notify("No ID found")
            self.close()
        self.actor_listitems = CreateListItems(actors, 0)
        self.crew_listitems = CreateListItems(crew, 0)
        self.similar_movies_listitems = CreateListItems(similar_movies, 0)
        self.list_listitems = CreateListItems(lists, 0)
        self.studio_listitems = CreateListItems(production_companies, 0)
        self.releases_listitems = CreateListItems(releases, 0)
        self.genre_listitems = CreateListItems(genres, 0)
        self.keyword_listitems = CreateListItems(keywords, 0)
        self.review_listitems = CreateListItems(reviews, 0)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        self.getControl(50).addItems(self.actor_listitems)
        self.getControl(150).addItems(self.similar_movies_listitems)
        self.getControl(250).addItems(self.set_listitems)
        self.getControl(350).addItems(self.youtube_listitems)
        self.getControl(450).addItems(self.list_listitems)
        self.getControl(550).addItems(self.studio_listitems)
        self.getControl(650).addItems(self.releases_listitems)
        self.getControl(750).addItems(self.crew_listitems)
        self.getControl(850).addItems(self.genre_listitems)
        self.getControl(950).addItems(self.keyword_listitems)
        self.getControl(1050).addItems(self.review_listitems)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlID):
        homewindow.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if controlID in [50, 750]:
            actorid = self.getControl(controlID).getSelectedItem().getProperty("id")
            AddToWindowStack("video", self.MovieId)
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % __addonname__, __cwd__, id=actorid)
            self.close()
            dialog.doModal()
        elif controlID in [150, 250]:
            movieid = self.getControl(controlID).getSelectedItem().getProperty("id")
            self.close()
            AddToWindowStack("video", self.MovieId)
            dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=movieid)
            dialog.doModal()
        elif controlID == 350:
            listitem = self.getControl(350).getSelectedItem()
            self.close()
            PlayTrailer(listitem.getProperty("youtube_id"))
        elif controlID == 550:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            studioitems = GetCompanyInfo(self.getControl(controlID).getSelectedItem().getProperty("id"))
            AddToWindowStack("video", self.MovieId)
            self.close()
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=studioitems)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        elif controlID == 950:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            keywordid = self.getControl(controlID).getSelectedItem().getProperty("id")
            keyworditems = GetMoviesWithKeyword(keywordid)
            AddToWindowStack("video", self.MovieId)
            self.close()
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=keyworditems)
            dialog.doModal()
        elif controlID == 850:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            genreid = self.getControl(controlID).getSelectedItem().getProperty("id")
            genreitems = GetMoviesWithGenre(genreid)
            AddToWindowStack("video", self.MovieId)
            self.close()
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=genreitems)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        elif controlID == 650:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            country = self.getControl(controlID).getSelectedItem().getProperty("iso_3166_1")
            certification = self.getControl(controlID).getSelectedItem().getProperty("certification")
            cert_items = GetMoviesWithCertification(country, certification)
            AddToWindowStack("video", self.MovieId)
            self.close()
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=cert_items)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        elif controlID == 450:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            list_items = GetMoviesFromList(self.getControl(controlID).getSelectedItem().getProperty("id"))
            self.close()
            AddToWindowStack("video", self.MovieId)
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=list_items)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        elif controlID == 6001:
            rating = xbmcgui.Dialog().input( "Enter Rating (0 - 20)", "", type=xbmcgui.INPUT_NUMERIC )
            rating = float(rating) / 2.0
            RateMovie(self.MovieId, rating)
        elif controlID == 6002:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            list_items = GetRatedMovies()
            self.close()
            AddToWindowStack("video", self.MovieId)
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=list_items)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()
        elif controlID == 6003:
            AddItemToFavourites(self.movie["ID"])
        elif controlID == 6004:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            list_items = GetFavMovies()
            self.close()
            AddToWindowStack("video", self.MovieId)
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % __addonname__, __cwd__, listitems=list_items)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            dialog.doModal()



    def onFocus(self, controlID):
        pass
