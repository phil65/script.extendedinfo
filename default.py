import sys
import xbmc, xbmcgui, xbmcaddon
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')

def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

class Main:
    def __init__( self ):
        log("version %s started" % __addonversion__ )
        self._init_vars()
        self._parse_argv()
        # run in backend if parameter was set
        if xbmc.getCondVisibility("IsEmpty(Window(home).Property(artistalbums_backend_running))"):
            if self.backend:
                xbmc.executebuiltin('SetProperty(artistalbums_backend_running,true,home)')
                self.run_backend()
            # only set new properties if artistid is not smaller than 0, e.g. -1
            elif self.artistid and self.artistid > -1:
                self._set_albums(self.artistid)
            # else clear old properties
            else:
                self._clear_properties()
            
    def _init_vars(self):
        self.window = xbmcgui.Window(10502) # Music Library Window
        self.cleared = False

    def _parse_argv(self):
        try:
            params = dict( arg.split("=") for arg in sys.argv[1].split("&"))
        except:
            params = {}
        log("params: %s" % params)
        self.artistid = -1
        try: self.artistid = int(params.get("artistid", "-1"))
        except: pass
        self.backend = params.get("backend", False)
        self.type = str(params.get("type", False))

    def run_backend(self):
        self._stop = False
        self.previousitem = ""
        while not self._stop:
            if not xbmc.getCondVisibility("Container.Scrolling"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if xbmc.getInfoLabel("ListItem.DBID") > -1:
                        self._set_albums(xbmc.getInfoLabel("ListItem.DBID"))
                    else:
                        self._clear_properties()
            else:
                self._clear_properties()
            xbmc.sleep(100)
            if not xbmc.getCondVisibility("Window.IsVisible(musiclibrary)"):
                self._clear_properties()
                xbmc.executebuiltin('ClearProperty(artistalbums_backend_running,home)')
                self._stop = True

    def _set_albums( self, dbid ):
        try:
            if xbmc.getCondVisibility('Container.Content(artists)') or self.type == "artist":
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "year", "thumbnail"], "sort": { "method": "label" }, "filter": {"artistid": %s} }, "id": 1}' % dbid)
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                log(json_query)
                json_response = simplejson.loads(json_query)
                if json_response['result'].has_key('albums'):
                    self._set_properties(json_response['result']['albums'])
        except:
            pass
            
    def _set_properties( self, audio ):
        # Set album properties
        count = 1
        # Clear properties before setting new ones
        self._clear_properties()
        for item in audio:
            self.window.setProperty('AlbumTitle.%d' % count, item['title'])
            self.window.setProperty('AlbumYear.%d' % count, str(item['year']))
            self.window.setProperty('AlbumThumb.%d' % count, item['thumbnail'])
            self.window.setProperty('AlbumID.%d' % count, str(item.get('albumid')))
            count += 1
        count = 1
        self.cleared = False
                
    def _clear_properties( self ):
        if not self.cleared:
            for i in range(1,50):
                self.window.clearProperty('AlbumTitle.%d' % i)
                self.window.clearProperty('AlbumYear.%d' % i)
                self.window.clearProperty('AlbumThumb.%d' % i)
                self.window.clearProperty('AlbumID.%d' % i)
            self.cleared = True

if ( __name__ == "__main__" ):
    Main()
log('finished')
