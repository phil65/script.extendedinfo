import os
import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id')).decode("utf-8"))
homewindow = xbmcgui.Window(10000)


class DialogActorInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.id = kwargs.get('id')
        name = kwargs.get('name')
        if not self.id and name:
            names = name.split(" / ")
            if len(names) > 1:
                Dialog = xbmcgui.Dialog()
                ret = Dialog.select("test", names)
                Notify(str(ret))
            self.id = GetPersonID(name)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        if self.id:
            self.person, self.movie_roles, self.tvshow_roles, self.images = GetExtendedActorInfo(self.id)
        name = self.person["name"]
        self.youtube_vids = GetYoutubeSearchVideos(name)
        homewindow.setProperty("actor.Title", name)
        homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
        homewindow.setProperty("actor.Biography", self.person["biography"])
        homewindow.setProperty("actor.Birthday", self.person["birthday"])
        homewindow.setProperty("actor.Thumb", self.person["thumb"])
        homewindow.setProperty("actor.id", self.person["id"])
        homewindow.setProperty("actor.AlsoKnownAs", self.person["also_known_as"])
        homewindow.setProperty("actor.Description", self.person["description"])
        homewindow.setProperty("actor.PlaceOfBirth", self.person["place_of_birth"])
        homewindow.setProperty("actor.DeathDay", self.person["deathday"])
        homewindow.setProperty("actor.Homepage", self.person["homepage"])
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
