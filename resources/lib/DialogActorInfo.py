import xbmc
import xbmcgui
from Utils import *
from ImageTools import *
from TheMovieDB import *
from YouTube import *
import DialogVideoInfo
import DialogTVShowInfo
from BaseClasses import DialogBaseInfo


class DialogActorInfo(DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(DialogActorInfo, self).__init__(*args, **kwargs)
        self.id = kwargs.get('id', False)
        if not self.id:
            name = kwargs.get('name').decode("utf-8").split(" " + xbmc.getLocalizedString(20347) + " ")
            names = name[0].strip().split(" / ")
            if len(names) > 1:
                ret = xbmcgui.Dialog().select(ADDON.getLocalizedString(32027), names)
                if ret == -1:
                    return None
                name = names[ret]
            else:
                name = names[0]
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            self.id = GetPersonID(name)
            if self.id:
                self.id = self.id["id"]
            else:
                return None
        if not self.id:
            Notify(ADDON.getLocalizedString(32143))
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            return None
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.data = GetExtendedActorInfo(self.id)
        youtube_thread = Get_Youtube_Vids_Thread(self.data["general"]["name"], "", "relevance", 15)
        youtube_thread.start()
        filter_thread = Filter_Image_Thread(self.data["general"]["thumb"], 25)
        filter_thread.start()
        db_movies = 0
        for item in self.data["movie_roles"]:
            if "DBID" in item:
                db_movies += 1
        self.data["general"]["DBMovies"] = str(db_movies)
        filter_thread.join()
        self.data["general"]['ImageFilter'], self.data["general"]['ImageColor'] = filter_thread.image, filter_thread.imagecolor
        youtube_thread.join()
        self.listitems = [(150, create_listitems(self.data["movie_roles"], 0)),
                          (250, create_listitems(self.data["tvshow_roles"], 0)),
                          (450, create_listitems(self.data["images"], 0)),
                          (550, create_listitems(self.data["movie_crew_roles"], 0)),
                          (650, create_listitems(self.data["tvshow_crew_roles"], 0)),
                          (750, create_listitems(self.data["tagged_images"], 0)),
                          (350, create_listitems(youtube_thread.listitems, 0))]
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        super(DialogActorInfo, self).onInit()
        HOME.setProperty("actor.ImageColor", self.data["general"]["ImageColor"])
        passDictToSkin(self.data["general"], "actor.", False, False, self.windowid)
        self.fill_lists()

    def onClick(self, controlID):
        HOME.setProperty("WindowColor", xbmc.getInfoLabel("Window(home).Property(ActorInfo.ImageColor)"))
        if controlID in [150, 550]:
            listitem = self.getControl(controlID).getSelectedItem()
            AddToWindowStack(self)
            self.close()
            dialog = DialogVideoInfo.DialogVideoInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=listitem.getProperty("id"), dbid=listitem.getProperty("dbid"))
            dialog.doModal()
        elif controlID in [250, 650]:
            listitem = self.getControl(controlID).getSelectedItem()
            # options = [ADDON.getLocalizedString(32147), ADDON.getLocalizedString(32148)]
            # selection = xbmcgui.Dialog().select(ADDON.getLocalizedString(32151), options)
            # if selection == 0:
            #     GetCreditInfo(listitem.getProperty("credit_id"))
            # if selection == 1:
            AddToWindowStack(self)
            self.close()
            dialog = DialogTVShowInfo.DialogTVShowInfo(u'script-%s-DialogVideoInfo.xml' % ADDON_NAME, ADDON_PATH, id=listitem.getProperty("id"), dbid=listitem.getProperty("dbid"))
            dialog.doModal()
        elif controlID in [450, 750]:
            image = self.getControl(controlID).getSelectedItem().getProperty("original")
            dialog = SlideShow(u'script-%s-SlideShow.xml' % ADDON_NAME, ADDON_PATH, image=image)
            dialog.doModal()
        elif controlID == 350:
            listitem = self.getControl(controlID).getSelectedItem()
            AddToWindowStack(self)
            self.close()
            self.movieplayer.playYoutubeVideo(listitem.getProperty("youtube_id"), listitem, True)
            self.movieplayer.wait_for_video_end()
            PopWindowStack()
        elif controlID == 132:
            text = self.data["general"]["biography"]
            w = TextViewer_Dialog('DialogTextViewer.xml', ADDON_PATH, header=ADDON.getLocalizedString(32037), text=text, color=self.data["general"]['ImageColor'])
            w.doModal()
