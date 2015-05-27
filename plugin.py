import sys
import os
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
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
from Utils import *


class Main:

    def __init__(self):
        xbmc.log("version %s started" % ADDON_VERSION)
        xbmc.executebuiltin('SetProperty(extendedinfo_running,True,home)')
        # try:
        self._parse_argv()
        if self.infos:
            StartInfoActions(self.infos, self.params)
        else:
            movie = {"intheaters": "RottenTomatoes: In theaters",
                     "boxoffice": "RottenTomatoes: Box office",
                     "opening": "RottenTomatoes: Opening movies",
                     "comingsoon": "RottenTomatoes: Upcoming movies",
                     "toprentals": "RottenTomatoes: Top rentals",
                     "currentdvdreleases": "RottenTomatoes: Current DVD releases",
                     "newdvdreleases": "RottenTomatoes: New DVD releases",
                     "upcomingdvds": "RottenTomatoes: Upcoming DVDs",
                     # tmdb
                     "incinemas": "TheMovieDB: In-cinema Movies",
                     "upcoming": "TheMovieDB: Upcoming movies",
                     "topratedmovies": "TheMovieDB: Top rated movies",
                     "popularmovies": "TheMovieDB: Popular movies",
                     # trakt
                     "trendingmovies": "Trakt.tv: Trending movies",
                     # tmdb
                     "starredmovies": "TheMovieDB: %s" % ADDON.getLocalizedString(32134),
                     "ratedmovies": "TheMovieDB: %s" % ADDON.getLocalizedString(32135),
                     # local
                     # "latestdbmovies": "Local DB: Latest movies",
                     # "randomdbmovies": "Local DB: Random movies",
                     # "inprogressdbmovies": "Local DB: In progress movies",
                     }
            # xbmcplugin.setContent(self.handle, 'files')

            # url = 'plugin://script.extendedinfo?info=extendedinfo&&id=233'
            # li = xbmcgui.ListItem('TheMovieDB database browser', iconImage='DefaultMovies.png')
            # xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li)
            for key, value in movie.iteritems():
                li = xbmcgui.ListItem(value, iconImage='DefaultFolder.png')
                url = 'plugin://script.extendedinfo?info=%s' % key
                xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                            listitem=li, isFolder=True)
            xbmcplugin.endOfDirectory(self.handle)
        xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')
        # except Exception:
        #     xbmc.executebuiltin('Dialog.Close(busydialog)')
        #     buggalo.onExceptionRaised()
        #     xbmc.executebuiltin('ClearProperty(extendedinfo_running,home)')

    def _parse_argv(self):
        args = sys.argv[2][1:].split("&&")
        self.handle = int(sys.argv[1])
        self.control = "plugin"
        self.infos = []
        self.params = {"handle": self.handle,
                       "control": self.control}
        for arg in args:
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
