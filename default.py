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
addon_strings = addon.getLocalizedString
addon_path = addon.getAddonInfo('path').decode("utf-8")
addon_libs = xbmc.translatePath(os.path.join(addon_path, 'resources', 'lib')).decode("utf-8")
sys.path.append(addon_libs)
from process import StartInfoActions
from Utils import *


class Main:

    def __init__(self):
        log("version %s started" % addon_version)
        xbmc.executebuiltin('SetProperty(extendedinfo_running,True,home)')
        self._init_vars()
        self._parse_argv()
        # run in backend if parameter was set
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
        self.pluginmode = False

    def _parse_argv(self):
        if sys.argv[0] == 'plugin://script.extendedinfo/':
            self.pluginmode = True
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
            log(param)
            if param.startswith('info='):
                self.infos.append(param[5:])
            else:
                try:
                    self.params[param.split("=")[0].lower()] = param.split("=")[1].strip()
                except:
                    pass

if (__name__ == "__main__"):
    Main()
log('finished')
