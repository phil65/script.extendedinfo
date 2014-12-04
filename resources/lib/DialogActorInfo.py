import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from TheMovieDB import *
from YouTube import *
import DialogVideoInfo
homewindow = xbmcgui.Window(10000)

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")


class DialogActorInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.id = kwargs.get('id')
        if not self.id:
            name = kwargs.get('name')
            name = name.decode("utf-8")
            name = name.split(xbmc.getLocalizedString(20347))
            name = name[0].strip().encode("utf-8")
            names = name.split(" / ")
            if len(names) > 1:
                Dialog = xbmcgui.Dialog()
                ret = Dialog.select("Actor Info", names)
                if ret == -1:
                    return False
                name = names[ret]
            self.id = GetPersonID(name)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        xbmc.sleep(500)
        self.person = None
        self.movie_roles = None
        self.tvshow_roles = None
        self.images = None
        if self.id:
            self.person, self.movie_roles, self.tvshow_roles, self.images = GetExtendedActorInfo(self.id)
            name = self.person["name"]
            self.youtube_vids = GetYoutubeSearchVideosV3(name)
            self.youtube_listitems = CreateListItems(self.youtube_vids, 0)
            self.movie_listitems = CreateListItems(self.movie_roles, 0)
            self.tvshow_listitems = CreateListItems(self.tvshow_roles, 0)
            self.image_listitems = CreateListItems(self.images)
     #       prettyprint(self.person)
            passHomeDataToSkin(self.person, "actor.")
            homewindow.setProperty("actor.TotalMovies", str(len(self.movie_roles)))
        else:
            Notify("No ID found")
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        if not self.id:
            self.close()
        self.getControl(150).addItems(self.movie_listitems)
        self.getControl(250).addItems(self.tvshow_listitems)
        self.getControl(350).addItems(self.youtube_listitems)
        self.getControl(450).addItems(self.image_listitems)
    #    self.getControl(150).addItems(tvshow_listitems)

    def setControls(self):
        pass

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()

    def onClick(self, controlID):
        homewindow.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(ActorInfo.ImageColor)"))
        if controlID in [150, 250]:
            listitem = self.getControl(controlID).getSelectedItem()
            AddToWindowStack("actor", self.id)
            dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=listitem.getProperty("id"), dbid=listitem.getProperty("dbid"))
            self.close()
            dialog.doModal()
        elif controlID == 350:
            listitem = self.getControl(350).getSelectedItem()
            self.close()
            xbmc.executebuiltin("PlayMedia(%s)" % listitem.getProperty("Path"))

    def onFocus(self, controlID):
        pass
