import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
import DialogVideoInfo
homewindow = xbmcgui.Window(10000)

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_strings = addon.getLocalizedString
addon_path = addon.getAddonInfo('path').decode("utf-8")


class DialogVideoList(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.listitem_list = kwargs.get('listitems')
        self.color = kwargs.get('dialogcolor')
        if not self.color:
            self.color = "FFAAAAAA"
        self.listitems = CreateListItems(self.listitem_list)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        windowid = xbmcgui.getCurrentWindowDialogId()
        xbmcgui.Window(windowid).setProperty("WindowColor", self.color)
        self.getControl(500).addItems(self.listitems)
        xbmc.sleep(200)
        xbmc.executebuiltin("SetFocus(500)")

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlID):
        if controlID in [500]:
            AddToWindowStack(self)
            media_id = self.getControl(controlID).getSelectedItem().getProperty("id")
            self.close()
            dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=media_id)
            dialog.doModal()

    def onFocus(self, controlID):
        pass
