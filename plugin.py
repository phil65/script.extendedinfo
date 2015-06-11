# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

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
from process import start_info_actions
from Utils import *


class Main:

    def __init__(self):
        xbmc.log("version %s started" % ADDON_VERSION)
        xbmc.executebuiltin('SetProperty(extendedinfo_running,True,home)')
        # try:
        self._parse_argv()
        if self.infos:
            start_info_actions(self.infos, self.params)
        else:
            movie = {"intheaters": "In theaters [I](RottenTomatoes)[/I]",
                     "boxoffice": "Box office [I](RottenTomatoes)[/I]",
                     "opening": "Opening movies [I](RottenTomatoes)[/I]",
                     "comingsoon": "Upcoming movies [I](RottenTomatoes)[/I]",
                     "toprentals": "Top rentals [I](RottenTomatoes)[/I]",
                     "currentdvdreleases": "Current DVD releases [I](RottenTomatoes)[/I]",
                     "newdvdreleases": "New DVD releases [I](RottenTomatoes)[/I]",
                     "upcomingdvds": "Upcoming DVDs [I](RottenTomatoes)[/I]",
                     # tmdb
                     "incinemas": "In-cinema Movies [I](TheMovieDB)[/I]",
                     "upcoming": "Upcoming movies [I](TheMovieDB)[/I]",
                     "topratedmovies": "Top rated movies [I](TheMovieDB)[/I]",
                     "popularmovies": "Popular movies [I](TheMovieDB)[/I]",
                     "accountlists": "User-created lists [I](TheMovieDB)[/I]",
                     # trakt
                     "trendingmovies": "Trending movies [I](Trakt.tv)[/I]",
                     # tmdb
                     "starredmovies": "%s [I](TheMovieDB)[/I]" % ADDON.getLocalizedString(32134),
                     "ratedmovies": "%s [I](TheMovieDB)[/I]" % ADDON.getLocalizedString(32135),
                     }
            tvshow = {"airingshows": "Airing TV shows [I](Trakt.tv)[/I]",
                      "premiereshows": "Premiere TV shows [I](Trakt.tv)[/I]",
                      "trendingshows": "Trending TV shows [I](Trakt.tv)[/I]",
                      "airingtodaytvshows": "TV shows airing today [I](TheMovieDB)[/I]",
                      "onairtvshows": "TV shows on air [I](TheMovieDB)[/I]",
                      "topratedtvshows": "Top rated TV shows [I](TheMovieDB)[/I]",
                      "populartvshows": "Popular TV shows [I](TheMovieDB)[/I]",
                      "starredtvshows": "%s [I](TheMovieDB)[/I]" % ADDON.getLocalizedString(32144),
                      "ratedtvshows": "%s [I](TheMovieDB)[/I]" % ADDON.getLocalizedString(32145),
                      }

            xbmcplugin.setContent(self.handle, 'files')

            # url = 'plugin://script.extendedinfo?info=extendedinfo&&id=233'
            # li = xbmcgui.ListItem('TheMovieDB database browser', iconImage='DefaultMovies.png')
            # xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li)
            items = merge_dicts(movie, tvshow)
            for key, value in items.iteritems():
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
        args = sys.argv[2][1:]
        self.handle = int(sys.argv[1])
        self.control = "plugin"
        self.infos = []
        self.params = {"handle": self.handle,
                       "control": self.control}
        if args.startswith("---"):
            delimiter = "&"
            args = args[3:]
        else:
            delimiter = "&&"
        for arg in args.split(delimiter):
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
