import os
import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))
homewindow = xbmcgui.Window(10000)


class DialogVideoInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.id = kwargs.get('id')
        self.dbid = kwargs.get('dbid')
        name = kwargs.get('name')
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        if self.id:
            self.movie, self.actors = GetExtendedMovieInfo(self.id)
            name = self.movie["Title"]
            self.youtube_vids = GetYoutubeSearchVideos(name)
            passHomeDataToSkin(self.movie, "movie.")
         #   homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
        else:
            Notify("No ID found")
        self.actor_listitems = CreateListItems(self.actors, 5)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        xbmc.executebuiltin("SetFocus(8)")
        self.getControl(50).addItems(self.actor_listitems)
    #    self.getControl(150).addItems(tvshow_listitems)


    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
