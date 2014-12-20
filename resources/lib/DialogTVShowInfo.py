import xbmc
import xbmcaddon
import xbmcgui
from Utils import *
from ImageTools import *
from TheMovieDB import *
from YouTube import *
import DialogActorInfo
import DialogVideoList
import DialogSeasonInfo
homewindow = xbmcgui.Window(10000)

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
addon_strings = addon.getLocalizedString
addon_path = addon.getAddonInfo('path').decode("utf-8")


class DialogTVShowInfo(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [92, 9]
    ACTION_EXIT_SCRIPT = [13, 10]

    def __init__(self, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.movieplayer = VideoPlayer(popstack=True)
        xbmcgui.WindowXMLDialog.__init__(self)
        tmdb_id = kwargs.get('id')
        dbid = kwargs.get('dbid')
        imdb_id = kwargs.get('imdbid')
        tvdb_id = kwargs.get('tvdb_id')
        if tmdb_id:
            self.tmdb_id = tmdb_id
        elif dbid and (int(dbid) > -1):
            tvdb_id = GetImdbIDFromDatabase("tvshow", dbid)
            self.tmdb_id = Get_Show_TMDB_ID(tvdb_id)
            log("IMDBId from local DB:" + str(self.tmdb_id))
        elif tvdb_id:
            self.tmdb_id = Get_Show_TMDB_ID(tvdb_id)
        elif imdb_id:
            self.tmdb_id = Get_Show_TMDB_ID(imdb_id, "imdb_id")
        elif self.name:
            self.tmdb_id = search_movie(kwargs.get('name'))
        else:
            self.tmdb_id = ""
        if self.tmdb_id:
            self.tvshow = GetExtendedTVShowInfo(self.tmdb_id)
            if not self.tvshow:
                self.close()
            log("Blur image %s with radius %i" % (self.tvshow["general"]["Thumb"], 25))
            image, imagecolor = Filter_Image(self.tvshow["general"]["Thumb"], 25)
            self.tvshow["general"]['ImageFilter'] = image
            self.tvshow["general"]['ImageColor'] = imagecolor
            self.youtube_vids = GetYoutubeSearchVideosV3(self.tvshow["general"]["Title"] + " tv", "", "relevance", 15)
        else:
            Notify("No ID found")
            self.close()
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        homewindow.setProperty("movie.ImageColor", self.tvshow["general"]["ImageColor"])
        windowid = xbmcgui.getCurrentWindowDialogId()
        xbmcgui.Window(windowid).setProperty("tmdb_logged_in", checkLogin())
        passDictToSkin(self.tvshow["general"], "movie.", False, False, windowid)
        self.getControl(1000).addItems(CreateListItems(self.tvshow["actors"], 0))
        self.getControl(150).addItems(CreateListItems(self.tvshow["similar"], 0))
        self.getControl(250).addItems(CreateListItems(self.tvshow["seasons"], 0))
        self.getControl(550).addItems(CreateListItems(self.tvshow["studios"], 0))
        self.getControl(1450).addItems(CreateListItems(self.tvshow["networks"], 0))
        self.getControl(750).addItems(CreateListItems(self.tvshow["crew"], 0))
        self.getControl(850).addItems(CreateListItems(self.tvshow["genres"], 0))
        self.getControl(950).addItems(CreateListItems(self.tvshow["keywords"], 0))
        self.getControl(1150).addItems(CreateListItems(self.tvshow["videos"], 0))
        self.getControl(350).addItems(CreateListItems(self.youtube_vids, 0))
        self.getControl(1250).addItems(CreateListItems(self.tvshow["images"], 0))
        self.getControl(1350).addItems(CreateListItems(self.tvshow["backdrops"], 0))

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()
            PopWindowStack()
        elif action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlID):
        homewindow.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(movie.ImageColor)"))
        if controlID in [1000, 750]:
            actorid = self.getControl(controlID).getSelectedItem().getProperty("id")
            AddToWindowStack(self)
            dialog = DialogActorInfo.DialogActorInfo(u'script-%s-DialogInfo.xml' % addon_name, addon_path, id=actorid)
            self.close()
            dialog.doModal()
        elif controlID in [150]:
            tmdb_id = self.getControl(controlID).getSelectedItem().getProperty("id")
            self.close()
            AddToWindowStack(self)
            dialog = DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=tmdb_id)
            dialog.doModal()
        elif controlID in [250]:
            season = self.getControl(controlID).getSelectedItem().getProperty("Season")
            self.close()
            AddToWindowStack(self)
            dialog = DialogSeasonInfo.DialogSeasonInfo(u'script-%s-DialogVideoInfo.xml' % addon_name, addon_path, id=self.tmdb_id, season=season, tvshow=self.tvshow["general"]["Title"])
            dialog.doModal()
        elif controlID in [350, 1150]:
            listitem = self.getControl(controlID).getSelectedItem()
            AddToWindowStack(self)
            self.close()
            self.movieplayer.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, True)
            self.movieplayer.WaitForVideoEnd()
        elif controlID == 550:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = GetCompanyInfo(self.getControl(controlID).getSelectedItem().getProperty("id"))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.OpenVideoList(listitems)
        elif controlID == 950:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = GetMoviesWithKeyword(self.getControl(controlID).getSelectedItem().getProperty("id"))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.OpenVideoList(listitems)
        elif controlID == 850:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = GetTVShowsWithGenre(self.getControl(controlID).getSelectedItem().getProperty("id"))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.OpenVideoList(listitems)
        elif controlID in [1250, 1350]:
            image = self.getControl(controlID).getSelectedItem().getProperty("Poster")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % addon_name, addon_path, image=image)
            dialog.doModal()
        elif controlID == 1450:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            listitems = GetTVShowsFromNetwork(self.getControl(controlID).getSelectedItem().getProperty("id"))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            self.OpenVideoList(listitems)
        elif controlID == 6003:
            ChangeFavStatus(self.tvshow["general"]["ID"], "tv", "true")
        elif controlID == 132:
            w = TextViewer_Dialog('DialogTextViewer.xml', addon_path, header="Overview", text=self.tvshow["general"]["Plot"], color=self.tvshow["general"]['ImageColor'])
            w.doModal()
        # elif controlID == 650:
        #     xbmc.executebuiltin("ActivateWindow(busydialog)")
        #     country = self.getControl(controlID).getSelectedItem().getProperty("iso_3166_1")
        #     certification = self.getControl(controlID).getSelectedItem().getProperty("certification")
        #     cert_items = GetMoviesWithCertification(country, certification)
        #     AddToWindowStack(self)
        #     self.close()
        #     dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % addon_name, addon_path, listitems=cert_items)
        #     xbmc.executebuiltin("Dialog.Close(busydialog)")
        #     dialog.doModal()
        # elif controlID == 450:
        #     xbmc.executebuiltin("ActivateWindow(busydialog)")
        #     list_items = GetMoviesFromList(self.getControl(controlID).getSelectedItem().getProperty("id"))
        #     self.close()
        #     AddToWindowStack(self)
        #     dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % addon_name, addon_path, listitems=list_items)
        #     xbmc.executebuiltin("Dialog.Close(busydialog)")
        #     dialog.doModal()

    def onFocus(self, controlID):
        pass

    def OpenVideoList(self, listitems):
        AddToWindowStack(self)
        self.close()
        dialog = DialogVideoList.DialogVideoList(u'script-%s-VideoList.xml' % addon_name, addon_path, listitems=listitems, color=self.tvshow["general"]['ImageColor'])
        dialog.doModal()
