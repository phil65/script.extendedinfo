# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import sys
import xbmc
import xbmcplugin
import xbmcgui
import routing
from resources.lib.process import start_info_actions
from resources.lib.Utils import *
plugin = routing.Plugin()


class Main:

    def __init__(self):
        xbmc.log("version %s started" % ADDON_VERSION)
        HOME.setProperty("extendedinfo_running", "true")
        self._parse_argv()
        for info in self.infos:
            listitems = start_info_actions(info, self.params)
            if info.endswith("shows"):
                xbmcplugin.setContent(plugin.handle, 'tvshows')
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
            elif info.endswith("episodes"):
                xbmcplugin.setContent(plugin.handle, 'episodes')
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)

            elif info.endswith("movies"):
                xbmcplugin.setContent(plugin.handle, 'movies')
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
                xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
            elif info.endswith("lists"):
                xbmcplugin.setContent(plugin.handle, 'sets')
            else:
                xbmcplugin.setContent(plugin.handle, '')
            pass_list_to_skin(name=info,
                              data=listitems,
                              prefix=self.params.get("prefix", ""),
                              handle=plugin.handle,
                              limit=self.params.get("limit", 20))
            break
        else:
            plugin.run()
        HOME.clearProperty("extendedinfo_running")

    def _parse_argv(self):
        args = sys.argv[2][1:]
        self.infos = []
        self.params = {"handle": plugin.handle}
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
                    self.params[param.split("=")[0].lower()] = "=".join(param.split("=")[1:]).strip().decode('utf-8')
                except:
                    pass


@plugin.route('/rotten_tomatoes')
def rotten_tomatoes():
    xbmcplugin.setPluginCategory(plugin.handle, "Rotten Tomatoes")
    items = {"intheatermovies": "%s" % LANG(32042),
             "boxofficemovies": "%s" % LANG(32055),
             "openingmovies": "%s" % LANG(32048),
             "comingsoonmovies": "%s" % LANG(32043),
             "toprentalmovies": "%s" % LANG(32056),
             "currentdvdmovies": "%s" % LANG(32049),
             "newdvdmovies": "%s" % LANG(32053),
             "upcomingdvdmovies": "%s" % LANG(32054)}
    for key, value in items.iteritems():
        li = xbmcgui.ListItem(value, iconImage='DefaultFolder.png')
        url = 'plugin://script.extendedinfo?info=%s' % key
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/tmdb')
def tmdb():
    items = {"incinemamovies": LANG(32042),
             "upcomingmovies": LANG(32043),
             "topratedmovies": LANG(32046),
             "popularmovies": LANG(32044),
             "accountlists": LANG(32045),
             "starredmovies": LANG(32134),
             "ratedmovies": LANG(32135),
             "airingtodaytvshows": LANG(32038),
             "onairtvshows": LANG(32039),
             "topratedtvshows": LANG(32040),
             "populartvshows": LANG(32041),
             "starredtvshows": LANG(32144),
             "ratedtvshows": LANG(32145)}
    for key, value in items.iteritems():
        li = xbmcgui.ListItem(value, iconImage='DefaultFolder.png')
        url = 'plugin://script.extendedinfo?info=%s' % key
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/trakt')
def trakt():
    items = {"trendingmovies": LANG(32047),
             "airingepisodes": LANG(32028),
             "premiereepisodes": LANG(32029),
             "trendingshows": LANG(32032)}
    for key, value in items.iteritems():
        li = xbmcgui.ListItem(value, iconImage='DefaultFolder.png')
        url = 'plugin://script.extendedinfo?info=%s' % key
        xbmcplugin.addDirectoryItem(handle=plugin.handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/')
def root():
    items = [
        (plugin.url_for(trakt), xbmcgui.ListItem("Trakt"), True),
        (plugin.url_for(rotten_tomatoes), xbmcgui.ListItem("Rotten Tomatoes"), True),
        (plugin.url_for(tmdb), xbmcgui.ListItem("TheMovieDB"), True),
    ]
    xbmcplugin.addDirectoryItems(plugin.handle, items)
    xbmcplugin.endOfDirectory(plugin.handle)

if (__name__ == "__main__"):
    Main()
xbmc.log('finished')
