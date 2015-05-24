import xbmc
import xbmcgui
from Utils import *
from YouTube import *
from BaseClasses import DialogBaseList
HOME = xbmcgui.Window(10000)


class DialogYoutubeList(DialogBaseList):

    def __init__(self, *args, **kwargs):
        super(DialogYoutubeList, self).__init__()
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
            self.totalitems = len(self.listitem_list)
        else:
            self.update_content(force_update=force)
            # Notify(str(self.totalpages))
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
            PopWindowStack()
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
                ChangeFavStatus(item_id, self.type, "true")
            elif selection == 2:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                listitems = [ADDON.getLocalizedString(32139)]
                account_lists = GetAccountLists()
                for item in account_lists:
                    listitems.append("%s (%i)" % (item["name"], item["item_count"]))
                listitems.append(ADDON.getLocalizedString(32138))
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32136), listitems)
                if index == 0:
                    listname = xbmcgui.Dialog().input(ADDON.getLocalizedString(32137), type=xbmcgui.INPUT_ALPHANUM)
                    if listname:
                        list_id = CreateList(listname)
                        xbmc.sleep(1000)
                        ChangeListStatus(list_id, item_id, True)
                elif index == len(listitems) - 1:
                    self.RemoveListDialog(account_lists)
                elif index > 0:
                    ChangeListStatus(account_lists[index - 1]["id"], item_id, True)
                    # xbmc.sleep(2000)
                    # self.update_content(force_update=True)
                    # self.update_ui()
            elif selection == 3:
                ChangeListStatus(self.list_id, item_id, False)
                self.update_content(force_update=True)
                self.update_ui()

    def onClick(self, controlID):
        if controlID in [500]:
            AddToWindowStack(self)
            self.close()

    def add_filter(self, key, value, typelabel, label):
        self.force_overwrite = False
        super(DialogYoutubeList, self).add_filter(key, value, typelabel, label)

    def fetch_data(self, force=False):
        return GetYoutubeSearchVideos("test"), "20", "20"
