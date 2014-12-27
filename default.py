import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_path = addon.getAddonInfo('path').decode("utf-8")
sys.path.append(xbmc.translatePath(os.path.join(addon_path, 'resources', 'lib')).decode("utf-8"))
from process import StartInfoActions


class Main:

    def __init__(self):
        xbmc.log("version %s started" % addon_version)
        xbmc.executebuiltin('SetProperty(extendedinfo_running,True,home)')
        self._init_vars()
        self._parse_argv()
        if self.infos:
            StartInfoActions(self.infos, self.params)
        if self.control == "plugin":
            xbmcplugin.endOfDirectory(self.handle)
        xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')

    def _init_vars(self):
        self.window = xbmcgui.Window(10000)  # Home Window
        self.control = None
        self.infos = []
        self.handle = None

    def _parse_argv(self):
        if sys.argv[0] == 'plugin://script.extendedinfo/':
            args = sys.argv[2][1:].split("&&")
            self.handle = int(sys.argv[1])
            self.control = "plugin"
        else:
            args = sys.argv
        self.params = {"handle": self.handle,
                       "control": self.control}
        for arg in args:
            if arg == 'script.extendedinfo':
                continue
            param = arg.replace('"', '').replace("'", " ")
            if param.startswith('info='):
                self.infos.append(param[5:])
            else:
                try:
                    self.params[param.split("=")[0].lower()] = param.split("=")[1].strip()
                except:
                    pass

if (__name__ == "__main__"):
    Main()
xbmc.log('finished')
