import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogVideoList
from ImageTools import *
homewindow = xbmcgui.Window(10000)

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_strings = addon.getLocalizedString
addon_path = addon.getAddonInfo('path').decode("utf-8")


class DialogEpisodeInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        xbmcgui.WindowXMLDialog.__init__(self)
        self.movieplayer = VideoPlayer(popstack=True)
        self.tmdb_id = kwargs.get('show_id')
        self.season = kwargs.get('season')
        self.showname = kwargs.get('tvshow')
        self.episode = kwargs.get('episode')
        self.logged_in = checkLogin()
        prettyprint(kwargs)
        if self.tmdb_id or self.showname:
            self.episode = GetExtendedEpisodeInfo(self.tmdb_id, self.season, self.episode)
            prettyprint(self.episode)
            if not self.episode:
                self.close()
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            search_string = "%s %s tv" % (self.episode["general"]["TVShowTitle"], self.episode["general"]["Title"])
            youtube_thread = Get_Youtube_Vids_Thread(search_string, "", "relevance", 15)
            youtube_thread.start()
            if not "DBID" in self.episode["general"]: # need to add comparing for episodes
                # Notify("download Poster")
                poster_thread = Get_ListItems_Thread(Get_File, self.episode["general"]["Thumb"])
                poster_thread.start()
            if not "DBID" in self.episode["general"]:
                poster_thread.join()
                self.episode["general"]['Poster'] = poster_thread.listitems
            filter_thread = Filter_Image_Thread(self.episode["general"]["Poster"], 25)
            filter_thread.start()
            youtube_thread.join()
            self.youtube_vids = youtube_thread.listitems
            filter_thread.join()
            self.episode["general"]['ImageFilter'], self.episode["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
        else:
            Notify("No ID found")
            self.close()
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        homewindow.setProperty("movie.ImageColor", self.episode["general"]["ImageColor"])
        windowid = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(windowid)
        self.window.setProperty("type", "episode")
        passDictToSkin(self.episode["general"], "movie.", False, False, windowid)
        self.getControl(1000).addItems(CreateListItems(self.episode["actors"], 0))
        self.getControl(750).addItems(CreateListItems(self.episode["crew"], 0))
        self.getControl(1150).addItems(CreateListItems(self.episode["videos"], 0))
        self.getControl(350).addItems(CreateListItems(self.youtube_vids, 0))
        self.getControl(1250).addItems(CreateListItems(self.episode["images"], 0))


    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlID):
        homewindow.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if controlID in [1000, 750]:
            actorid = self.getControl(controlID).getSelectedItem().getProperty("id")
            AddToWindowStack(self)
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % addon_name, addon_path, id=actorid)
            self.close()
            dialog.doModal()
        elif controlID in [2000]:
            episode = self.getControl(controlID).getSelectedItem().getProperty("episode")
            AddToWindowStack(self)
            dialog = DialogEpisodeInfo.DialogEpisodeInfo(u'script-%s-DialogInfo.xml' % addon_name, addon_path, id=actorid)
            self.close()
            dialog.doModal()
        elif controlID in [350, 1150]:
            listitem = self.getControl(controlID).getSelectedItem()
            AddToWindowStack(self)
            self.close()
            self.movieplayer.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, True)
            self.movieplayer.WaitForVideoEnd()
            PopWindowStack()
        elif controlID in [1250, 1350]:
            image = self.getControl(controlID).getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % addon_name, addon_path, image=image)
            dialog.doModal()
        elif controlID == 132:
            w = TextViewer_Dialog('DialogTextViewer.xml', addon_path, header="Overview", text=self.season["general"]["Plot"], color=self.season["general"]['ImageColor'])
            w.doModal()


    def onFocus(self, controlID):
        pass

    def OpenVideoList(self, listitems):
        AddToWindowStack(self)
        self.close()
        dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % addon_name, addon_path, listitems=listitems)
        dialog.doModal()
