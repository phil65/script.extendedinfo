import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import datetime
import urllib2
import os
import sys
import time
import gzip
from StringIO import StringIO

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % __addonid__).decode("utf-8"))

window = xbmcgui.Window(10000)
wnd = xbmcgui.Window(12003)
locallist = []


def AddArtToLibrary(type, media, folder, limit, silent=False):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get%ss", "params": {"properties": ["art", "file"], "sort": { "method": "label" } }, "id": 1}' % media.lower())
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if (json_response['result'] is not None) and ('%ss' % (media.lower()) in json_response['result']):
        # iterate through the results
        if not silent:
            progressDialog = xbmcgui.DialogProgress(__language__(32016))
            progressDialog.create(__language__(32016))
        for count, item in enumerate(json_response['result']['%ss' % media.lower()]):
            if not silent:
                if progressDialog.iscanceled():
                    return
            path = os.path.join(media_path(item['file']).encode("utf-8"), folder)
            file_list = xbmcvfs.listdir(path)[1]
            for i, file in enumerate(file_list):
                if i + 1 > limit:
                    break
                if not silent:
                    progressDialog.update((count * 100) / json_response['result']['limits']['total'], __language__(32011) + ' %s: %s %i' % (item["label"], type, i + 1))
                    if progressDialog.iscanceled():
                        return
                # just in case someone uses backslahes in the path
                # fixes problems mentioned on some german forum
                file_path = os.path.join(path, file).encode('string-escape')
                if xbmcvfs.exists(file_path) and item['art'].get('%s%i' % (type, i), '') == "":
                    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Set%sDetails", "params": { "%sid": %i, "art": { "%s%i": "%s" }}, "id": 1 }' % (media, media.lower(), item.get('%sid' % media.lower()), type, i + 1, file_path))


def import_skinsettings():
    importstring = read_from_file()
    if importstring:
        progressDialog = xbmcgui.DialogProgress(__language__(32010))
        progressDialog.create(__language__(32010))
        xbmc.sleep(200)
        for count, skinsetting in enumerate(importstring):
            if progressDialog.iscanceled():
                return
            if skinsetting[1].startswith(xbmc.getSkinDir()):
                progressDialog.update((count * 100) / len(importstring), __language__(32011) + ' %s' % skinsetting[1])
                setting = skinsetting[1].replace(xbmc.getSkinDir() + ".", "")
                if skinsetting[0] == "string":
                    if skinsetting[2] is not "":
                        xbmc.executebuiltin("Skin.SetString(%s,%s)" % (setting, skinsetting[2]))
                    else:
                        xbmc.executebuiltin("Skin.Reset(%s)" % setting)
                elif skinsetting[0] == "bool":
                    if skinsetting[2] == "true":
                        xbmc.executebuiltin("Skin.SetBool(%s)" % setting)
                    else:
                        xbmc.executebuiltin("Skin.Reset(%s)" % setting)
            xbmc.sleep(30)
        xbmcgui.Dialog().ok(__language__(32005), __language__(32009))
    else:
        log("backup not found")


def export_skinsettings():
    from xml.dom.minidom import parse
    # Set path
    guisettings_path = xbmc.translatePath('special://profile/guisettings.xml').decode("utf-8")
    # Check to see if file exists
    if xbmcvfs.exists(guisettings_path):
        log("guisettings.xml found")
        doc = parse(guisettings_path)
        skinsettings = doc.documentElement.getElementsByTagName('setting')
        newlist = []
        for count, skinsetting in enumerate(skinsettings):
            if skinsetting.childNodes:
                value = skinsetting.childNodes[0].nodeValue
            else:
                value = ""
            if skinsetting.attributes['name'].nodeValue.startswith(xbmc.getSkinDir()):
                newlist.append((skinsetting.attributes['type'].nodeValue, skinsetting.attributes['name'].nodeValue, value))
        if save_to_file(newlist, xbmc.getSkinDir() + ".backup"):
            xbmcgui.Dialog().ok(__language__(32005), __language__(32006))
    else:
        xbmcgui.Dialog().ok(__language__(32007), __language__(32008))
        log("guisettings.xml not found")


def GetXBMCArtists():
    filename = Addon_Data_Path + "/XBMCartists.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 0:
        return read_from_file(filename)
    else:
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["musicbrainzartistid","thumbnail"]}, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query = simplejson.loads(json_query)
        save_to_file(json_query, "XBMCartists", Addon_Data_Path)
        return json_query


def GetSimilarArtistsInLibrary(id):
    from LastFM import GetSimilarById
    simi_artists = GetSimilarById(id)
    if simi_artists is None:
        log('Last.fm didn\'t return proper response')
        return None
    xbmc_artists = GetXBMCArtists()
    artists = []
    for (count, simi_artist) in enumerate(simi_artists):
        for (count, xbmc_artist) in enumerate(xbmc_artists["result"]["artists"]):
            if xbmc_artist['musicbrainzartistid'] != '':
                if xbmc_artist['musicbrainzartistid'] == simi_artist['mbid']:
                    artists.append(xbmc_artist)
            elif xbmc_artist['artist'] == simi_artist['name']:
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtistDetails", "params": {"properties": ["genre", "description", "mood", "style", "born", "died", "formed", "disbanded", "yearsactive", "instrument", "fanart", "thumbnail"], "artistid": %s}, "id": 1}' % str(xbmc_artist['artistid']))
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                json_response = simplejson.loads(json_query)
                item = json_response["result"]["artistdetails"]
                newartist = {"Title"       : item['label'],
                             "Genre"       : " / ".join(item['genre']),
                             "Thumb"       : item['thumbnail'], #remove
                             "Fanart"      : item['fanart'], #remove
                             "Art(thumb)"  : item['thumbnail'],
                             "Art(fanart)" : item['fanart'],
                             "Description" : item['description'],
                             "Born"        : item['born'],
                             "Died"        : item['died'],
                             "Formed"      : item['formed'],
                             "Disbanded"   : item['disbanded'],
                             "YearsActive" : " / ".join(item['yearsactive']),
                             "Style"       : " / ".join(item['style']),
                             "Mood"        : " / ".join(item['mood']),
                             "Instrument"  : " / ".join(item['instrument']),
                             "LibraryPath" : 'musicdb://artists/' + str(item['artistid']) + '/' }                         
                artists.append(newartist)
    log('%i of %i artists found in last.FM is in XBMC database' % (len(artists), len(simi_artists)))
    return artists


def create_light_movielist():
    # if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 1:
        # return read_from_file(filename)
    if True:
        a = datetime.datetime.now()
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["set", "originaltitle", "imdbnumber", "file"], "sort": { "method": "random" } }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query = simplejson.loads(json_query)
        b = datetime.datetime.now() - a
        log('Processing Time for fetching JSON light movielist: %s' % b)
        a = datetime.datetime.now()
        b = datetime.datetime.now() - a
        log('Processing Time for save light movielist: %s' % b)
        return json_query


def GetSimilarFromOwnLibrary(dbid):
    movies = []
#    # if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 1:
        # return read_from_file(filename)
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["genre","director","country","year","mpaa"], "movieid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if "moviedetails" in json_response['result']:
        id = json_response['result']['moviedetails']['movieid']
        genres = json_response['result']['moviedetails']['genre']
        year = int(json_response['result']['moviedetails']['year'])
        countries = json_response['result']['moviedetails']['country']
        directors = json_response['result']['moviedetails']['director']
        mpaa = json_response['result']['moviedetails']['mpaa']
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["genre","director","mpaa","country","year"], "sort": { "method": "random" } }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query = simplejson.loads(json_query)
        if "movies" in json_query['result']:
            quotalist = []
            for item in json_query['result']['movies']:
                difference = int(item['year']) - year
                hit = 0.0
                miss = 0.0
                quota = 0.0
                for genre in genres:
                    if genre in item['genre']:
                        hit += 1.0
                    else:
                        miss += 1.0
                miss += 0.00001
                if hit > 0.0:
                    quota = float(hit) / float(hit + miss)
                if genres[0] == item['genre'][0]:
                    quota += 0.3
                if difference < 6 and difference > -6:
                    quota += 0.15
                if difference < 3 and difference > -3:
                    quota += 0.15
                if countries[0] == item['country'][0]:
                    quota += 0.4
                if mpaa == item['mpaa']:
                    quota += 0.4
                if directors[0] == item['director'][0]:
                    quota += 0.6
                quotalist.append((quota, item["movieid"]))
            if True:
                quotalist = sorted(quotalist, key=lambda quota: quota[0], reverse=True)
                count = 1
                for list_movie in quotalist:
                    if id is not list_movie[1]:
                        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["genre", "imdbnumber", "year", "art", "rating"], "movieid":%s }, "id": 1}' % str(list_movie[1]))
                        json_query = unicode(json_query, 'utf-8', errors='ignore')
                        json_response = simplejson.loads(json_query)
                        movie = json_response["result"]["moviedetails"]
                        newmovie = {'Art(fanart)': movie["art"].get('fanart', ""),
                                    'Art(poster)': movie["art"].get('poster', ""),
                                    'Title': movie.get('label', ""),
                                    'OriginalTitle': movie.get('originaltitle', ""),
                                    'ID': movie.get('imdbnumber', ""),
                                    'Path': "",
                                    'Play': "",
                                    'DBID': str(movie['movieid']),
                                    'Rating': str(round(float(movie['rating']), 1)),
                                    'Premiered': movie.get('year', "")}
                        movies.append(newmovie)
                        count += 1
                        if count > 20:
                            break
            return movies


def media_streamdetails(filename, streamdetails):
    info = {}
    video = streamdetails['video']
    audio = streamdetails['audio']
    if '3d' in filename:
        info['videoresolution'] = '3d'
    elif video:
        videowidth = video[0]['width']
        videoheight = video[0]['height']
        if (videowidth <= 720 and videoheight <= 480):
            info['videoresolution'] = "480"
        elif (videowidth <= 768 and videoheight <= 576):
            info['videoresolution'] = "576"
        elif (videowidth <= 960 and videoheight <= 544):
            info['videoresolution'] = "540"
        elif (videowidth <= 1280 and videoheight <= 720):
            info['videoresolution'] = "720"
        elif (videowidth >= 1281 or videoheight >= 721):
            info['videoresolution'] = "1080"
        elif (videowidth >= 1921 or videoheight >= 1081):
            info['videoresolution'] = "4k"
        else:
            info['videoresolution'] = ""
    elif (('dvd') in filename and not ('hddvd' or 'hd-dvd') in filename) or (filename.endswith('.vob' or '.ifo')):
        info['videoresolution'] = '576'
    elif (('bluray' or 'blu-ray' or 'brrip' or 'bdrip' or 'hddvd' or 'hd-dvd') in filename):
        info['videoresolution'] = '1080'
    else:
        info['videoresolution'] = '1080'
    if video:
        info['videocodec'] = video[0]['codec']
        if (video[0]['aspect'] < 1.4859):
            info['videoaspect'] = "1.33"
        elif (video[0]['aspect'] < 1.7190):
            info['videoaspect'] = "1.66"
        elif (video[0]['aspect'] < 1.8147):
            info['videoaspect'] = "1.78"
        elif (video[0]['aspect'] < 2.0174):
            info['videoaspect'] = "1.85"
        elif (video[0]['aspect'] < 2.2738):
            info['videoaspect'] = "2.20"
        else:
            info['videoaspect'] = "2.35"
    else:
        info['videocodec'] = ''
        info['videoaspect'] = ''
    if audio:
        info['audiocodec'] = audio[0]['codec']
        info['audiochannels'] = audio[0]['channels']
    else:
        info['audiocodec'] = ''
        info['audiochannels'] = ''
    return info


def GetXBMCAlbums():
    albums = []
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title"]}, "id": 1}')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = simplejson.loads(json_query)
    if "result" in json_query and "albums" in json_query['result']:
        return json_query['result']['albums']
    else:
        return []


def media_path(path):
    # Check for stacked movies
    try:
        path = os.path.split(path)[0].rsplit(' , ', 1)[1].replace(",,", ",")
    except:
        path = os.path.split(path)[0]
    # Fixes problems with rared movies and multipath
    if path.startswith("rar://"):
        path = [os.path.split(urllib.url2pathname(path.replace("rar://", "")))[0]]
    elif path.startswith("multipath://"):
        temp_path = path.replace("multipath://", "").split('%2f/')
        path = []
        for item in temp_path:
            path.append(urllib.url2pathname(item))
    else:
        path = [path]
    return path[0]


def CompareWithLibrary(onlinelist):
    global locallist
    if not locallist:
        locallist = create_light_movielist()
    a = datetime.datetime.now()
    log("startin compare")
    for onlineitem in onlinelist:
        for localitem in locallist["result"]["movies"]:
            comparators = [localitem["originaltitle"], localitem["label"]]
            if onlineitem["OriginalTitle"] in comparators or onlineitem["Title"] in comparators:
       #         log("compare success" + onlineitem["Title"])
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["streamdetails","year"], "movieid":%s }, "id": 1}' % str(localitem["movieid"]))
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                json_response = simplejson.loads(json_query)
                if "moviedetails" in json_response["result"] and "Premiered" in onlineitem:
                    difference = int(onlineitem["Premiered"][:4]) - int(json_response['result']['moviedetails']['year'])
                    if difference > -2 and difference < 2:
                        streaminfo = media_streamdetails(localitem['file'].encode('utf-8').lower(), json_response['result']['moviedetails']['streamdetails'])
                        onlineitem.update({"Play": localitem["movieid"]})
                        onlineitem.update({"DBID": localitem["movieid"]})
                        onlineitem.update({"Path": localitem["movieid"]})
                        onlineitem.update({"VideoCodec": streaminfo["videocodec"]})
                        onlineitem.update({"VideoResolution": streaminfo["videoresolution"]})
                        onlineitem.update({"VideoAspect": streaminfo["videoaspect"]})
                        onlineitem.update({"AudioCodec": streaminfo["audiocodec"]})
                        onlineitem.update({"AudioChannels": str(streaminfo["audiochannels"])})
                break
    b = datetime.datetime.now() - a
    log('Processing Time for comparing: %s' % b)
    return onlinelist


def CompareAlbumWithLibrary(onlinelist):
    global locallist
    if not locallist:
        locallist = GetXBMCAlbums()
    a = datetime.datetime.now()
    log("startin compare")
    for onlineitem in onlinelist:
        for localitem in locallist:
            if onlineitem["name"] == localitem["title"]:
                log("compare success: " + onlineitem["name"])
                json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbumDetails", "params": {"properties": ["thumbnail"], "albumid":%s }, "id": 1}' % str(localitem["albumid"]))
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                json_query = simplejson.loads(json_query)
                album = json_query["result"]["albumdetails"]
                onlineitem.update({"DBID": album["albumid"]})
                onlineitem.update({"Path": 'XBMC.RunScript(service.skin.widgets,albumid=' + str(album["albumid"]) + ')'})
                if album["thumbnail"]:
                    log("updating " + album["thumbnail"])
                    onlineitem.update({"thumb": album["thumbnail"]})
                    onlineitem.update({"Icon": album["thumbnail"]})
               # onlineitem.update({"Path": localitem["movieid"]})
                break
    b = datetime.datetime.now() - a
    log('Processing Time for comparing: %s' % b)
    return onlinelist


def GetStringFromUrl(encurl):
    succeed = 0
    while succeed < 5:
        try:
            request = urllib2.Request(encurl)
            request.add_header('User-agent', 'XBMC/13.2 ( ptemming@gmx.net )')
            request.add_header('Accept-encoding', 'gzip')
            response = urllib2.urlopen(request)
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(response.read())
                compr = gzip.GzipFile(fileobj=buf)
                data = compr.read()
            else:
                data = response.read()
       #     log("URL String: " + data)
            return data
        except:
            log("GetStringFromURL: could not get data from %s" % encurl)
            xbmc.sleep(1000)
            succeed += 1
    return ""


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def get_browse_dialog(default="", heading="Browse", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse(dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default)
    return value


def save_to_file(content, filename, path=""):
    import xbmcvfs
    if path == "":
        text_file_path = get_browse_dialog() + filename + ".txt"
    else:
        if not xbmcvfs.exists(path):
            xbmcvfs.mkdir(path)
        text_file_path = os.path.join(path, filename + ".txt")
    log("save to textfile: " + text_file_path)
    text_file = xbmcvfs.File(text_file_path, "w")
    simplejson.dump(content, text_file)
    text_file.close()
    return True


def read_from_file(path=""):
    import xbmcvfs
    log("trying to load " + path)
    if path == "":
        path = get_browse_dialog(dlg_type=1)
    if xbmcvfs.exists(path):
        f = open(path)
        fc = simplejson.load(f)
        log("loaded textfile " + path)
        return fc
    else:
        return False


def ConvertYoutubeURL(string):
    import re
    if 'youtube.com/v' in string:
        vid_ids = re.findall('http://www.youtube.com/v/(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            convertedstring = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return convertedstring
    if 'youtube.com/watch' in string:
        vid_ids = re.findall('youtube.com/watch\?v=(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            convertedstring = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return convertedstring
    return ""


def ExtractYoutubeID(string):
    import re
    if 'youtube.com/v' in string:
        vid_ids = re.findall('http://www.youtube.com/v/(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            return id
    if 'youtube.com/watch' in string:
        vid_ids = re.findall('youtube.com/watch\?v=(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            return id
    return ""


def Notify(header, line='', line2='', line3=''):
    xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % (header, line, line2, line3))


def GetMovieSetName(dbid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["setid"], "movieid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if "moviedetails" in json_response["result"]:
        dbsetid = json_response['result']['moviedetails'].get('setid', "")
        if dbsetid:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid":%s }, "id": 1}' % dbsetid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = simplejson.loads(json_query)
            return json_response['result']['setdetails'].get('label', "")
    return ""


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))


def GetImdbID(type, dbid):
    if type=="movie":
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["imdbnumber","title", "year"], "movieid":%s }, "id": 1}' % dbid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if "moviedetails" in json_response["result"]:
            return json_response['result']['moviedetails']['imdbnumber']
        else:
            return []
    elif type == "tvshow":
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"properties": ["imdbnumber","title", "year"], "tvshowid":%s }, "id": 1}' % dbid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if "tvshowdetails" in json_response["result"]:
            return json_response['result']['tvshowdetails']['imdbnumber']
        else:
            return []


def passHomeDataToSkin(data, debug = True):
    if data is not None:
        for (key, value) in data.iteritems():
            window.setProperty('%s' % (str(key)), unicode(value))
            if debug:
                log('%s' % (str(key)) + unicode(value))


def passDataToSkin(name, data, prefix="",debug = False):
    if data is not None:
       # log( "%s%s.Count = %s" % (prefix, name, str(len(data)) ) )
        for (count, result) in enumerate(data):
            if debug:
                log("%s%s.%i = %s" % (prefix, name, count + 1, str(result)))
            for (key, value) in result.iteritems():
                window.setProperty('%s%s.%i.%s' % (prefix, name, count + 1, str(key)), unicode(value))
                if debug:
                    log('%s%s.%i.%s --> ' % (prefix, name, count + 1, str(key)) + unicode(value))
        window.setProperty('%s%s.Count' % (prefix, name), str(len(data)))
    else:
        window.setProperty('%s%s.Count' % (prefix, name), '0')
        log("%s%s.Count = None" % (prefix, name))


def cleanText(text):
    import re
    text = re.sub('<br \/>', '[CR]', text)
    text = re.sub('<(.|\n|\r)*?>', '', text)
    text = re.sub('&quot;', '"', text)
    text = re.sub('&amp;', '&', text)
    text = re.sub('&gt;', '>', text)
    text = re.sub('&lt;', '<', text)
    text = re.sub('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.', '', text)
    return text.strip()
