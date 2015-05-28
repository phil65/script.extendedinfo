import sys
import os
import xbmc
import xbmcaddon
# try:
#     import buggalo
#     buggalo.GMAIL_RECIPIENT = "phil65@kodi.tv"
# except:
#     pass
ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
sys.path.append(xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib')).decode("utf-8"))
from process import StartInfoActions


class Main:

    def __init__(self):
        xbmc.log("version %s started" % ADDON_VERSION)
        xbmc.executebuiltin('SetProperty(extendedinfo_running,True,home)')
        # try:
        self._parse_argv()
        if self.infos:
            StartInfoActions(self.infos, self.params)
        elif not self.handle:
            import DialogVideoList
            dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % ADDON_NAME, ADDON_PATH)
            dialog.doModal()
        xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')
        # except Exception:
        #     xbmc.executebuiltin('Dialog.Close(busydialog)')
        #     buggalo.onExceptionRaised()
        #     xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')

    def _parse_argv(self):
        self.handle = None
        self.infos = []
        self.params = {"handle": None,
                       "control": None}
        for arg in sys.argv:
            if arg == 'script.extendedinfo':
                continue
            param = arg.replace('"', '').replace("'", " ")
            if param.startswith('info='):
                self.infos.append(param[5:])
            else:
                try:
                    self.params[param.split("=")[0].lower()] = "=".join(param.split("=")[1:]).strip()
                except:
                    pass

if (__name__ == "__main__"):
    Main()
xbmc.log('finished')
