# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from Utils import *
from YouTube import *
from BaseClasses import DialogBaseList
from WindowManager import wm

class DialogYoutubeList(DialogBaseList):

    def __init__(self, *args, **kwargs):
        super(DialogYoutubeList, self).__init__(*args, **kwargs)
        self.layout = "landscape"
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.type = kwargs.get('type', "movie")
        self.search_string = kwargs.get('search_string', "")
        self.filter_label = kwargs.get("filter_label", "")
        self.mode = kwargs.get("mode", "filter")
        self.list_id = kwargs.get("list_id", False)
        self.sort = kwargs.get('sort', "popularity")
        self.sort_label = kwargs.get('sort_label', "Popularity")
        self.order = kwargs.get('order', "desc")
        force = kwargs.get('force', False)
        self.filters = kwargs.get('filters', [])
        if self.listitem_list:
            self.listitems = create_listitems(self.listitem_list)
            self.total_items = len(self.listitem_list)
        else:
            self.update_content(force_update=force)
            # notify(str(self.totalpages))
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def update_ui(self):
        super(DialogYoutubeList, self).update_ui()
        self.window.setProperty("Type", TRANSLATIONS[self.type])
        if self.type == "tv":
            self.window.getControl(5006).setVisible(False)
            self.window.getControl(5008).setVisible(False)
            self.window.getControl(5009).setVisible(False)
            self.window.getControl(5010).setVisible(False)
        else:
            self.window.getControl(5006).setVisible(True)
            self.window.getControl(5008).setVisible(True)
            self.window.getControl(5009).setVisible(True)
            self.window.getControl(5010).setVisible(True)

    def onAction(self, action):
        focusid = self.getFocusId()
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            wm.pop_stack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            if not focusid == 500:
                return None
            item_id = self.getControl(focusid).getSelectedItem().getProperty("id")
            if self.type == "tv":
                listitems = [ADDON.getLocalizedString(32169)]
            else:
                listitems = [ADDON.getLocalizedString(32113)]
            if self.logged_in:
                listitems += [xbmc.getLocalizedString(14076)]
                if not self.type == "tv":
                    listitems += [ADDON.getLocalizedString(32107)]
                if self.mode == "list":
                    listitems += [ADDON.getLocalizedString(32035)]
            # context_menu = ContextMenu.ContextMenu(u'DialogContextMenu.xml', ADDON_PATH, labels=listitems)
            # context_menu.doModal()
            selection = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), listitems)
            if selection == 0:
                rating = get_rating_from_user()
                if rating:
                    send_rating_for_media_item(self.type, item_id, rating)
                    xbmc.sleep(2000)
                    self.update_content(force_update=True)
                    self.update_ui()
            elif selection == 1:
                change_fav_status(item_id, self.type, "true")
            elif selection == 2:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                listitems = [ADDON.getLocalizedString(32139)]
                account_lists = get_account_lists()
                for item in account_lists:
                    listitems.append("%s (%i)" % (item["name"], item["item_count"]))
                listitems.append(ADDON.getLocalizedString(32138))
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
                if index == 0:
                    listname = xbmcgui.Dialog().input(ADDON.getLocalizedString(32137), type=xbmcgui.INPUT_ALPHANUM)
                    if listname:
                        list_id = create_list(listname)
                        xbmc.sleep(1000)
                        change_list_status(list_id, item_id, True)
                elif index == len(listitems) - 1:
                    self.remove_list_dialog(account_lists)
                elif index > 0:
                    change_list_status(account_lists[index - 1]["id"], item_id, True)
                    # xbmc.sleep(2000)
                    # self.update_content(force_update=True)
                    # self.update_ui()
            elif selection == 3:
                change_list_status(self.list_id, item_id, False)
                self.update_content(force_update=True)
                self.update_ui()

    def onClick(self, control_id):
        if control_id in [500]:
            wm.add_to_stack(self)
            self.close()

    def add_filter(self, key, value, typelabel, label):
        self.force_overwrite = False
        super(DialogYoutubeList, self).add_filter(key, value, typelabel, label)

    def fetch_data(self, force=False):
        return get_youtube_search_videos("test"), "20", "20"
