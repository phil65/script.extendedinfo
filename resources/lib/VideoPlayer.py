# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from WindowManager import wm


class VideoPlayer(xbmc.Player):

    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.stopped = False

    def onPlayBackEnded(self):
        self.stopped = True

    def onPlayBackStopped(self):
        self.stopped = True

    def onPlayBackStarted(self):
        self.stopped = False

    def play_youtube_video(self, youtube_id="", listitem=None, window=False):
        """
        play youtube vid with info from *listitem
        """
        if not listitem:
            listitem = xbmcgui.ListItem(xbmc.getLocalizedString(20410))
            listitem.setInfo(type='video',
                             infolabels={'title': xbmc.getLocalizedString(20410),
                                         xbmc.getLocalizedString(515): 'Youtube Video'})
        import YDStreamExtractor
        YDStreamExtractor.disableDASHVideo(True)
        if youtube_id:
            vid = YDStreamExtractor.getVideoInfo(youtube_id,
                                                 quality=1)
            if vid:
                if window and window.window_type == "dialog":
                    wm.add_to_stack(window)
                    window.close()
                stream_url = vid.streamURL()
                self.play(item=stream_url,
                          listitem=listitem)
                if window and window.window_type == "dialog":
                    self.wait_for_video_end()
                    wm.pop_stack()
        else:
            xbmcgui.Dialog().notification(heading=xbmc.getLocalizedString(257),
                                          message="no youtube id found")

    def wait_for_video_end(self):
        xbmc.sleep(500)
        while not self.stopped:
            xbmc.sleep(200)
        self.stopped = False
