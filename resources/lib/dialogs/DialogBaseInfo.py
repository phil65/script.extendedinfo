# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui

from resources.lib import TheMovieDB as tmdb
from resources.lib import YouTube
from resources.lib.WindowManager import wm

from kodi65 import addon
from kodi65 import utils
from kodi65 import kodijson
from kodi65 import selectdialog
from kodi65 import slideshow
from kodi65.listitem import ListItem
from ActionHandler import ActionHandler

ch = ActionHandler()

ID_LIST_YOUTUBE = 350
ID_LIST_VIDEOS = 1150
ID_LIST_IMAGES = 1250
ID_LIST_BACKDROPS = 1350
ID_BUTTON_BOUNCEUP = 20000
ID_BUTTON_BOUNCEDOWN = 20001


class DialogBaseInfo(object):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        super(DialogBaseInfo, self).__init__(*args, **kwargs)
        self.logged_in = tmdb.Login.check_login()
        self.dbid = kwargs.get('dbid')
        self.bouncing = False
        self.last_focus = None
        self.data = None
        self.yt_listitems = []
        self.info = ListItem()

    def onInit(self, *args, **kwargs):
        super(DialogBaseInfo, self).onInit()
        self.info.to_windowprops(window_id=self.window_id)
        for container_id, key in self.LISTS:
            try:
                self.getControl(container_id).reset()
                items = [i.get_listitem() for i in self.data[key]]
                self.getControl(container_id).addItems(items)
            except Exception:
                utils.log("Notice: No container with id %i available" % container_id)
        addon.set_global("ImageColor", self.info.get_property('ImageColor'))
        addon.set_global("infobackground", self.info.get_art('fanart_small'))
        self.setProperty("type", self.TYPE)
        self.setProperty("tmdb_logged_in", "true" if self.logged_in else "")

    def onAction(self, action):
        ch.serve_action(action, self.getFocusId(), self)

    def onClick(self, control_id):
        ch.serve(control_id, self)

    def onFocus(self, control_id):
        if control_id == ID_BUTTON_BOUNCEUP:
            if not self.bouncing:
                self.bounce("up")
            self.setFocusId(self.last_focus)
        elif control_id == ID_BUTTON_BOUNCEDOWN:
            if not self.bouncing:
                self.bounce("down")
            self.setFocusId(self.last_focus)
        self.last_focus = control_id

    @utils.run_async
    def bounce(self, identifier):
        self.bouncing = True
        self.setProperty("Bounce.%s" % identifier, "true")
        xbmc.sleep(200)
        self.clearProperty("Bounce.%s" % identifier)
        self.bouncing = False

    @ch.click(ID_LIST_IMAGES)
    @ch.click(ID_LIST_BACKDROPS)
    def open_image(self, control_id):
        key = [key for container_id, key in self.LISTS if container_id == control_id][0]
        listitems = self.data[key]
        pos = slideshow.open_slideshow(listitems=listitems,
                                       index=self.getControl(control_id).getSelectedPosition())
        self.getControl(control_id).selectItem(pos)

    @ch.click_by_type("video")
    def play_youtube_video(self, control_id):
        wm.play_youtube_video(youtube_id=self.FocusedItem(control_id).getProperty("youtube_id"),
                              listitem=self.FocusedItem(control_id),
                              window=self)

    @ch.click_by_type("artist")
    def open_actor_info(self, control_id):
        wm.open_actor_info(prev_window=self,
                           actor_id=self.FocusedItem(control_id).getProperty("id"))

    @ch.click_by_type("movie")
    def open_movie_info(self, control_id):
        wm.open_movie_info(prev_window=self,
                           movie_id=self.FocusedItem(control_id).getProperty("id"),
                           dbid=self.FocusedItem(control_id).getProperty("dbid"))

    @ch.click_by_type("tvshow")
    def open_tvshow_dialog(self, control_id):
        wm.open_tvshow_info(prev_window=self,
                            tmdb_id=self.FocusedItem(control_id).getProperty("id"),
                            dbid=self.FocusedItem(control_id).getProperty("dbid"))

    @ch.action("contextmenu", ID_LIST_IMAGES)
    def thumbnail_options(self, control_id):
        if not self.info.get("dbid"):
            return None
        selection = xbmcgui.Dialog().contextmenu(list=[addon.LANG(32006)])
        if selection == 0:
            kodijson.set_art(media_type=self.getProperty("type"),
                             art={"poster": self.FocusedItem(control_id).getProperty("original")},
                             dbid=self.info.get_property("dbid"))

    @ch.action("contextmenu", ID_LIST_BACKDROPS)
    def fanart_options(self, control_id):
        if not self.info.get("dbid"):
            return None
        selection = xbmcgui.Dialog().contextmenu(list=[addon.LANG(32007)])
        if selection == 0:
            kodijson.set_art(media_type=self.getProperty("type"),
                             art={"fanart": self.FocusedItem(control_id).getProperty("original")},
                             dbid=self.info.get_property("dbid"))

    @ch.context("video")
    def video_context_menu(self, control_id):
        selection = xbmcgui.Dialog().contextmenu(list=[addon.LANG(33003)])
        if selection == 0:
            utils.download_video(self.FocusedItem(control_id).getProperty("youtube_id"))

    @ch.context("movie")
    def movie_context_menu(self, control_id):
        movie_id = self.FocusedItem(control_id).getProperty("id")
        dbid = self.FocusedItem(control_id).getVideoInfoTag().getDbId()
        options = [addon.LANG(32113)]
        if self.logged_in:
            options.append(addon.LANG(32083))
        selection = xbmcgui.Dialog().contextmenu(list=options)
        if selection == 0:
            rating = utils.input_userrating()
            tmdb.set_rating(media_type="movie",
                            media_id=movie_id,
                            rating=rating,
                            dbid=dbid)
            xbmc.sleep(2000)
            tmdb.extended_movie_info(movie_id=movie_id,
                                     dbid=dbid,
                                     cache_time=0)
        elif selection == 1:
            account_lists = tmdb.get_account_lists()
            if not account_lists:
                return False
            listitems = ["%s (%i)" % (i["name"], i["item_count"]) for i in account_lists]
            i = xbmcgui.Dialog().select(addon.LANG(32136), listitems)
            if i > -1:
                tmdb.change_list_status(list_id=account_lists[i]["id"],
                                        movie_id=movie_id,
                                        status=True)

    @ch.context("artist")
    def person_context_menu(self, control_id):
        listitem = self.FocusedItem(control_id)
        options = [addon.LANG(32009), addon.LANG(32070)]
        credit_id = listitem.getProperty("credit_id")
        if credit_id and self.TYPE == "TVShow":
            options.append(addon.LANG(32147))
        selection = xbmcgui.Dialog().contextmenu(list=options)
        if selection == 0:
            wm.open_actor_info(prev_window=self,
                               actor_id=listitem.getProperty("id"))
        if selection == 1:
            filters = [{"id": listitem.getProperty("id"),
                        "type": "with_people",
                        "typelabel": addon.LANG(32156),
                        "label": listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)
        if selection == 2:
            self.open_credit_dialog(credit_id)

    @ch.context("tvshow")
    def tvshow_context_menu(self, control_id):
        credit_id = self.FocusedItem(control_id).getProperty("credit_id")
        options = [addon.LANG(32148)]
        if credit_id:
            options.append(addon.LANG(32147))
        selection = xbmcgui.Dialog().contextmenu(list=options)
        if selection == 0:
            wm.open_tvshow_info(prev_window=self,
                                tmdb_id=self.FocusedItem(control_id).getProperty("id"),
                                dbid=self.FocusedItem(control_id).getProperty("dbid"))
        if selection == 1:
            self.open_credit_dialog(credit_id=credit_id)

    @ch.action("parentdir", "*")
    @ch.action("parentfolder", "*")
    def previous_menu(self, control_id):
        onback = self.getProperty("%i_onback" % control_id)
        if onback:
            xbmc.executebuiltin(onback)
        else:
            self.close()
            wm.pop_stack()

    @ch.action("previousmenu", "*")
    def exit_script(self, control_id):
        wm.cancel(self)

    @utils.run_async
    def get_youtube_vids(self, search_str):
        try:
            youtube_list = self.getControl(ID_LIST_YOUTUBE)
        except Exception:
            return None
        if not self.yt_listitems:
            result = YouTube.search(search_str, limit=15)
            self.yt_listitems = result.get("listitems", [])
            if "videos" in self.data:
                vid_ids = [item.get_property("key") for item in self.data["videos"]]
                self.yt_listitems = [i for i in self.yt_listitems if i.get_property("youtube_id") not in vid_ids]
        youtube_list.reset()
        youtube_list.addItems(utils.create_listitems(self.yt_listitems))

    def open_credit_dialog(self, credit_id):
        info = tmdb.get_credit_info(credit_id)
        listitems = []
        if "seasons" in info["media"]:
            listitems += tmdb.handle_seasons(info["media"]["seasons"])
        if "episodes" in info["media"]:
            listitems += tmdb.handle_episodes(info["media"]["episodes"])
        if not listitems:
            listitems += [{"label": addon.LANG(19055)}]
        listitem, index = selectdialog.open_selectdialog(header=addon.LANG(32151),
                                                         listitems=listitems)
        if listitem["mediatype"] == "episode":
            wm.open_episode_info(prev_window=self,
                                 season=listitems[index]["season"],
                                 episode=listitems[index]["episode"],
                                 tvshow_id=info["media"]["id"])
        elif listitem["mediatype"] == "season":
            wm.open_season_info(prev_window=self,
                                season=listitems[index]["season"],
                                tvshow_id=info["media"]["id"])

    def update_states(self):
        if not self.states:
            return None
        utils.dict_to_windowprops(data=tmdb.get_account_props(self.states),
                                  window_id=self.window_id)
