import xbmc
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogEpisodeInfo
from ImageTools import *
from BaseClasses import DialogBaseInfo


class DialogSeasonInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogSeasonInfo, self).__init__(*args, **kwargs)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.tmdb_id = kwargs.get('id')
        self.season = kwargs.get('season')
        self.showname = kwargs.get('tvshow')
        if self.tmdb_id or (self.season and self.showname):
            self.data = GetSeasonInfo(self.tmdb_id, self.showname, self.season)
            if not self.data:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                return
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            search_string = "%s %s tv" % (self.data["general"]["TVShowTitle"], self.data["general"]["Title"])
            youtube_thread = Get_Youtube_Vids_Thread(search_string, "", "relevance", 15)
            youtube_thread.start()
            if "DBID" not in self.data["general"]:  # need to add comparing for seasons
                poster_thread = Threaded_Function(Get_File, self.data["general"]["Poster"])
                poster_thread.start()
            if "DBID" not in self.data["general"]:
                poster_thread.join()
                self.data["general"]['Poster'] = poster_thread.listitems
            filter_thread = Filter_Image_Thread(self.data["general"]["Poster"], 25)
            filter_thread.start()
            youtube_thread.join()
            filter_thread.join()
            self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
            self.listitems = [(1000, create_listitems(self.data["actors"], 0)),
                              (750, create_listitems(self.data["crew"], 0)),
                              (2000, create_listitems(self.data["episodes"], 0)),
                              (1150, create_listitems(self.data["videos"], 0)),
                              (1250, create_listitems(self.data["images"], 0)),
                              (1350, create_listitems(self.data["backdrops"], 0)),
                              (350, create_listitems(youtube_thread.listitems, 0))]
        else:
            Notify(ADDON.getLocalizedString(32143))
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        super(DialogSeasonInfo, self).onInit()
        HOME.setProperty("movie.ImageColor", self.data["general"]["ImageColor"])
        self.window.setProperty("type", "season")
        passDictToSkin(self.data["general"], "movie.", False, False, self.windowid)
        self.fill_lists()

    def onClick(self, controlID):
        control = self.getControl(controlID)
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if controlID in [1000, 750]:
            actor_id = control.getSelectedItem().getProperty("id")
            credit_id = control.getSelectedItem().getProperty("credit_id")
            AddToWindowStack(self)
            self.close()
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % ADDON_NAME, ADDON_PATH, id=actor_id, credit_id=credit_id)
            dialog.doModal()
        elif controlID in [2000]:
            episode = control.getSelectedItem().getProperty("episode")
            season = control.getSelectedItem().getProperty("season")
            if not self.tmdb_id:
                response = GetMovieDBData("search/tv?query=%s&language=%s&" % (urllib.quote_plus(self.showname), ADDON.getSetting("LanguageID")), 30)
                self.tmdb_id = str(response['results'][0]['id'])
            AddToWindowStack(self)
            self.close()
            dialog = DialogEpisodeInfo.DialogEpisodeInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, show_id=self.tmdb_id, season=season, episode=episode)
            dialog.doModal()
        elif controlID in [350, 1150]:
            listitem = control.getSelectedItem()
            AddToWindowStack(self)
            self.close()
            self.movieplayer.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, True)
            self.movieplayer.wait_for_video_end()
            PopWindowStack()
        elif controlID in [1250, 1350]:
            image = control.getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif controlID == 132:
            w = TextViewer_Dialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=self.data["general"]["Plot"], color=self.data["general"]['ImageColor'])
            w.doModal()
