import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
homewindow = xbmcgui.Window(10000)

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")


class DialogVideoInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        xbmcgui.WindowXMLDialog.__init__(self)
        self.id = kwargs.get('id')
        self.dbid = kwargs.get('dbid')
        self.imdbid = kwargs.get('imdbid')
        name = kwargs.get('name')
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
            self.movie, actors, similar_movies, lists, production_companies, releases, crew, genres, keywords = GetExtendedMovieInfo(MovieId, self.dbid)
            self.youtube_vids = GetYoutubeSearchVideosV3(self.movie["Label"] + " " + self.movie["Year"], "", "relevance", 15)
            self.set_listitems = []
            self.youtube_listitems = CreateListItems(self.youtube_vids, 0)
            if self.movie["SetId"]:
                self.set_listitems = CreateListItems(GetSetMovies(self.movie["SetId"]))
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "videodb://movies/actors/", "media": "files"}, "id": 1}')
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = simplejson.loads(json_query)
            for db_actor in json_response["result"]["files"]:
                for movie_actor in actors:
                    if db_actor["label"] == movie_actor["name"]:
                        movie_actor.update({"dbid": db_actor["id"]})
                        json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "videodb://movies/actors/%i/", "media": "files"}, "id": 1}' % db_actor["id"])
                        json_query2 = unicode(json_query2, 'utf-8', errors='ignore')
                        json_response2 = simplejson.loads(json_query2)
                        numfiles = len(json_response2["result"]["files"])
                        movie_actor.update({"moviecount": numfiles})
            passHomeDataToSkin(self.movie, "movie.")
         #   homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
        else:
            Notify("No ID found")
        self.actor_listitems = CreateListItems(actors, 0)
        self.crew_listitems = CreateListItems(crew, 0)
        self.similar_movies_listitems = CreateListItems(similar_movies, 0)
        self.list_listitems = CreateListItems(lists, 0)
        self.studio_listitems = CreateListItems(production_companies, 0)
        self.releases_listitems = CreateListItems(releases, 0)
        self.genre_listitems = CreateListItems(genres, 0)
        self.keyword_listitems = CreateListItems(keywords, 0)
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

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID in [50, 750]:
            actorid = self.getControl(controlID).getSelectedItem().getProperty("id")
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % __addonname__, __cwd__, id=actorid)
            self.close()
            dialog.doModal()
        elif controlID in [150, 250]:
            movieid = self.getControl(controlID).getSelectedItem().getProperty("id")
            self.close()
            dialog = DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=movieid)
            dialog.doModal()
        elif controlID == 350:
            listitem = self.getControl(350).getSelectedItem()
            self.close()
            # xbmc.executebuiltin("Dialog.Close(movieinformation)")
            xbmc.executebuiltin("PlayMedia(%s)" % listitem.getProperty("Path"))

    def onFocus(self, controlID):
        pass
