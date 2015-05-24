import xbmc
import xbmcgui
from Utils import *
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
