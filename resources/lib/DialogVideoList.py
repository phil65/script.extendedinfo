import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
import DialogVideoInfo
homewindow = xbmcgui.Window(10000)

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")


class DialogVideoList(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.listitem_list = kwargs.get('listitems')
        self.listitems = CreateListItems(self.listitem_list)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        self.getControl(500).addItems(self.listitems)
        xbmc.sleep(200)
        xbmc.executebuiltin("SetFocus(500)")

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()

    def onClick(self, controlID):
        if controlID in [500]:
            AddToWindowStack("list", self.listitem_list)
            movieid = self.getControl(controlID).getSelectedItem().getProperty("id")
            self.close()
            dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % __addonname__, __cwd__, id=movieid)
            dialog.doModal()

    def onFocus(self, controlID):
        pass
