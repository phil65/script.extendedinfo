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
        name = kwargs.get('name')
        if not self.id and name:
            names = name.split(" / ")
            if len(names) > 1:
                Dialog = xbmcgui.Dialog()
                ret = Dialog.select("Actor Info", names)
                if ret == -1:
                    return False
                name = names[ret]
            clean_name = name.split(" as ")[0]
            self.id = GetPersonID(clean_name)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        if self.id:
            self.movie = GetExtendedMovieInfo(self.id)
            name = self.movie["Title"]
            self.youtube_vids = GetYoutubeSearchVideos(name)
            passHomeDataToSkin(self.movie, "movie.")
            homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
        else:
            Notify("No ID found")
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        movie_listitems = CreateListItems(self.movie_roles)
        tvshow_listitems = CreateListItems(self.tvshow_roles)
        image_listitems = CreateListItems(self.images)
        youtube_listitems = CreateListItems(self.youtube_vids)
        self.getControl(150).addItems(movie_listitems)
        # self.getControl(250).addItems(image_listitems)
        self.getControl(350).addItems(youtube_listitems)
        xbmc.executebuiltin("SetFocus(150)")
    #    self.getControl(150).addItems(tvshow_listitems)

    def setControls(self):
        pass

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
