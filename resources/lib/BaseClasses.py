import xbmc
import xbmcgui
from Utils import *
import DialogVideoList
from TheMovieDB import *
HOME = xbmcgui.Window(10000)


class DialogBaseList(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listitem_list = kwargs.get('listitems', None)
        self.color = kwargs.get('color', "FFAAAAAA")
        self.page = 1
        self.totalpages = 1
        self.totalitems = 0

    def onInit(self):
        HOME.setProperty("WindowColor", self.color)
        self.windowid = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.windowid)
        self.window.setProperty("WindowColor", self.color)
        self.window.setProperty("layout", self.layout)
        self.update_ui()
        xbmc.sleep(200)
        if self.totalitems > 0:
            xbmc.executebuiltin("SetFocus(500)")
        else:
            xbmc.executebuiltin("SetFocus(6000)")

    def set_filter_url(self):
        filter_list = []
        # prettyprint(self.filters)
        for item in self.filters:
            filter_list.append("%s=%s" % (item["type"], item["id"]))
        self.filter_url = "&".join(filter_list)
        if self.filter_url:
            self.filter_url += "&"

    def set_filter_label(self):
        filter_list = []
        # prettyprint(self.filters)
        for item in self.filters:
            filter_list.append("[COLOR FFAAAAAA]%s:[/COLOR] %s" % (item["typelabel"], item["label"].decode("utf-8").replace("|", " | ").replace(",", " + ")))
        self.filter_label = "  -  ".join(filter_list)

    def update_content(self, add=False, force_update=False):
        if add:
            self.old_items = self.listitems
        else:
            self.old_items = []
        self.listitems, self.totalpages, self.totalitems = self.fetch_data(force=force_update)
        self.listitems = self.old_items + create_listitems(self.listitems)

    def update_ui(self):
        self.getControl(500).reset()
        self.getControl(500).addItems(self.listitems)
        self.window.setProperty("TotalPages", str(self.totalpages))
        self.window.setProperty("TotalItems", str(self.totalitems))
        self.window.setProperty("CurrentPage", str(self.page))
        self.window.setProperty("Filter_Label", self.filter_label)
        self.window.setProperty("Sort_Label", self.sort_label)
        if self.page == self.totalpages:
            self.window.clearProperty("ArrowDown")
        else:
            self.window.setProperty("ArrowDown", "True")
        if self.page > 1:
            self.window.setProperty("ArrowUp", "True")
        else:
            self.window.clearProperty("ArrowUp")
        if self.order == "asc":
            self.window.setProperty("Order_Label", xbmc.getLocalizedString(584))
        else:
            self.window.setProperty("Order_Label", xbmc.getLocalizedString(585))

    def onFocus(self, controlID):
        if controlID == 600:
            if self.page < self.totalpages:
                self.page += 1
            else:
                self.page = 1
                return
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            self.update_content()
            self.update_ui()
            xbmc.executebuiltin("Dialog.Close(busydialog)")
        if controlID == 700:
            if self.page > 1:
                self.page -= 1
            else:
                return
            # else:
            #     self.page = self.totalpages
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            self.update_content()
            self.update_ui()
            xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onClick(self, controlID):
        if controlID == 5001:
            self.get_sort_type()
            self.update_content()
            self.update_ui()

    def add_filter(self, key, value, typelabel, label):
        index = -1
        new_filter = {"id": value,
                      "type": key,
                      "typelabel": typelabel,
                      "label": label}
        if new_filter in self.filters:
            return False
        for i, item in enumerate(self.filters):
            if item["type"] == key:
                index = i
                break
        if not value:
            return False
        if index > -1:
            if not self.force_overwrite:
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno(heading=xbmc.getLocalizedString(587), line1=ADDON.getLocalizedString(32106), nolabel="OR", yeslabel="AND")
                if ret:
                    self.filters[index]["id"] = self.filters[index]["id"] + "," + urllib.quote_plus(str(value))
                    self.filters[index]["label"] = self.filters[index]["label"] + "," + str(label)
                else:
                    self.filters[index]["id"] = self.filters[index]["id"] + "|" + urllib.quote_plus(str(value))
                    self.filters[index]["label"] = self.filters[index]["label"] + "|" + str(label)
            else:
                self.filters[index]["id"] = urllib.quote_plus(str(value))
                self.filters[index]["label"] = str(label)
        else:
            self.filters.append(new_filter)


class DialogBaseInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.logged_in = checkLogin()
        self.movieplayer = VideoPlayer(popstack=True)
        self.data = None

    def onInit(self, *args, **kwargs):
        self.windowid = xbmcgui.getCurrentWindowDialogId()
        self.window = xbmcgui.Window(self.windowid)
        self.window.setProperty("tmdb_logged_in", self.logged_in)
        if not self.data:
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.close()
            return

    def fill_lists(self):
        for container_id, listitems in self.listitems:
            try:
                self.getControl(container_id).reset()
                self.getControl(container_id).addItems(listitems)
            except:
                log("Notice: No container with id %i available" % container_id)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def OpenVideoList(self, listitems=None, filters=[], mode="filter", list_id=False, filter_label="", force=False, media_type="movie"):
        AddToWindowStack(self)
        self.close()
        dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % ADDON_NAME, ADDON_PATH, listitems=listitems, color=self.data["general"]['ImageColor'], filters=filters, mode=mode, list_id=list_id, force=force, filter_label=filter_label, type=media_type)
        dialog.doModal()
