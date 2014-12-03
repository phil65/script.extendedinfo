import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmcplugin
import urllib2
import os
import time
import hashlib
import simplejson
import re
import threading

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonicon__ = __addon__.getAddonInfo('icon')
__language__ = __addon__.getLocalizedString
Addon_Data_Path = os.path.join(xbmc.translatePath(
    "special://profile/addon_data/%s" % __addonid__).decode("utf-8"))
homewindow = xbmcgui.Window(10000)
id_list = []
title_list = []
originaltitle_list = []


def GetPlaylistStats(path):
    startindex = -1
    endindex = -1
    if (".xsp" in path) and ("special://" in path):
        startindex = path.find("special://")
        endindex = path.find(".xsp") + 4
    elif ("library://" in path):
        startindex = path.find("library://")
        endindex = path.rfind("/") + 1
    elif ("videodb://" in path):
        startindex = path.find("videodb://")
        endindex = path.rfind("/") + 1
    if (startindex > 0) and (endindex > 0):
        playlistpath = path[startindex:endindex]
    #    Notify(playlistpath)
    #   json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter": {"field": "path", "operator": "contains", "value": "%s"}, "properties": ["playcount", "resume"]}, "id": 1}' % (playlistpath))
        json_query = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "video", "properties": ["playcount", "resume"]}, "id": 1}' % (playlistpath))
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if "result" in json_response:
            played = 0
            inprogress = 0
            numitems = json_response["result"]["limits"]["total"]
            for item in json_response["result"]["files"]:
                if item["playcount"] > 0:
                    played += 1
                if item["resume"]["position"] > 0:
                    inprogress += 1
            homewindow.setProperty('PlaylistWatched', str(played))
            homewindow.setProperty('PlaylistUnWatched', str(numitems - played))
            homewindow.setProperty('PlaylistInProgress', str(inprogress))
            homewindow.setProperty('PlaylistCount', str(numitems))


def GetSortLetters(path, focusedletter):
    listitems = []
    letterlist = []
    homewindow.clearProperty("LetterList")
    if __addon__.getSetting("FolderPath") == path:
        letterlist = __addon__.getSetting("LetterList")
        letterlist = letterlist.split()
    else:
        if path:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "files"}, "id": 1}' % (path))
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = simplejson.loads(json_query)
            if "result" in json_response and "files" in json_response["result"]:
                for movie in json_response["result"]["files"]:
                    sortletter = movie["label"].replace("The ", "")[0]
                    if not sortletter in letterlist:
                        letterlist.append(sortletter)
            __addon__.setSetting("LetterList", " ".join(letterlist))
            __addon__.setSetting("FolderPath", path)
    homewindow.setProperty("LetterList", "".join(letterlist))
    if letterlist and focusedletter:
        startord = ord("A")
        for i in range(0, 26):
            letter = chr(startord + i)
            if letter == focusedletter:
                label = "[B][COLOR FFFF3333]%s[/COLOR][/B]" % letter
            elif letter in letterlist:
                label = letter
            else:
                label = "[COLOR 55FFFFFF]%s[/COLOR]" % letter
            listitem = {"label": label}
            listitems.append(listitem)
    return listitems


def GetXBMCArtists():
    filename = Addon_Data_Path + "/XBMCartists.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 0:
        return read_from_file(filename)
    else:
        json_query = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "params": {"properties": ["musicbrainzartistid","thumbnail"]}, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query = simplejson.loads(json_query)
        save_to_file(json_query, "XBMCartists", Addon_Data_Path)
        return json_query


def GetSimilarArtistsInLibrary(artistid):
    from LastFM import GetSimilarById
    simi_artists = GetSimilarById(artistid)
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
                json_query = xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtistDetails", "params": {"properties": ["genre", "description", "mood", "style", "born", "died", "formed", "disbanded", "yearsactive", "instrument", "fanart", "thumbnail"], "artistid": %s}, "id": 1}' % str(xbmc_artist['artistid']))
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                json_response = simplejson.loads(json_query)
                item = json_response["result"]["artistdetails"]
                newartist = {"Title": item['label'],
                             "Genre": " / ".join(item['genre']),
                             "Thumb": item['thumbnail'],  # remove
                             "Fanart": item['fanart'],  # remove
                             "Art(thumb)": item['thumbnail'],
                             "Art(fanart)": item['fanart'],
                             "Description": item['description'],
                             "Born": item['born'],
                             "Died": item['died'],
                             "Formed": item['formed'],
                             "Disbanded": item['disbanded'],
                             "YearsActive": " / ".join(item['yearsactive']),
                             "Style": " / ".join(item['style']),
                             "Mood": " / ".join(item['mood']),
                             "Instrument": " / ".join(item['instrument']),
                             "LibraryPath": 'musicdb://artists/' + str(item['artistid']) + '/'}
                artists.append(newartist)
    log('%i of %i artists found in last.FM is in XBMC database' %
        (len(artists), len(simi_artists)))
    return artists


def GetSimilarFromOwnLibrary(dbid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["genre","director","country","year","mpaa"], "movieid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if "moviedetails" in json_response['result']:
        movieid = json_response['result']['moviedetails']['movieid']
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
            quotalist = sorted(quotalist, key=lambda quota: quota[0], reverse=True)
            count = 1
            for list_movie in quotalist:
                if movieid is not list_movie[1]:
                    movies = []
                    newmovie = GetMovieFromDB(list_movie[1])
                    movies.append(newmovie)
                    count += 1
                    if count > 20:
                        break
            return movies

def GetMovieFromDB(movieid):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director", "writer", "cast", "dateadded", "imdbnumber"], "movieid":%s }, "id": 1}' % str(movieid))
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    movie = json_response["result"]["moviedetails"]
    newmovie = {'Art(fanart)': movie["art"].get('fanart', ""),
                'Art(poster)': movie["art"].get('poster', ""),
                'Fanart': movie["art"].get('fanart', ""),
                'Poster': movie["art"].get('poster', ""),
                'Title': movie.get('label', ""),
                'OriginalTitle': movie.get('originaltitle', ""),
                'ID': movie.get('imdbnumber', ""),
                'Path': "",
                'Play': "",
                'DBID': str(movie['movieid']),
                'Rating': str(round(float(movie['rating']), 1)),
                'Premiered': movie.get('year', "")}


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
    json_query = xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title"]}, "id": 1}')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = simplejson.loads(json_query)
    if "result" in json_query and "albums" in json_query['result']:
        return json_query['result']['albums']
    else:
        return []


def create_channel_list():
    json_response = xbmc.executeJSONRPC(
        '{"jsonrpc":"2.0","id":1,"method":"PVR.GetChannels","params":{"channelgroupid":"alltv", "properties": [ "thumbnail", "locked", "hidden", "channel", "lastplayed" ]}}')
    json_response = unicode(json_response, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_response)
    if ('result' in json_response) and ("movies" in json_response["result"]):
        return json_response
    else:
        return False


def fetch(dictionary, key):
    if key in dictionary:
        if dictionary[key] is not None:
            return dictionary[key]
    return ""


def CompareWithLibrary(onlinelist):
    global id_list
    global originaltitle_list
    global title_list
    if not title_list:
        now = time.time()
        title_list = xbmc.getInfoLabel("Window(home).Property(title_list.JSON)")
        if title_list:
            title_list = simplejson.loads(title_list)
            originaltitle_list = simplejson.loads(xbmc.getInfoLabel("Window(home).Property(originaltitle_list.JSON)"))
            id_list = simplejson.loads(xbmc.getInfoLabel("Window(home).Property(id_list.JSON)"))
        else:
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["originaltitle", "imdbnumber", "file"], "sort": { "method": "none" } }, "id": 1}')
            json_query = simplejson.loads(unicode(json_query, 'utf-8', errors='ignore'))
            id_list = []
            originaltitle_list = []
            title_list = []
            for item in json_query["result"]["movies"]:
                id_list.append(item["movieid"])
                originaltitle_list.append(item["originaltitle"].lower())
                title_list.append(item["label"].lower())

            homewindow.setProperty("id_list.JSON", simplejson.dumps(id_list))
            homewindow.setProperty("originaltitle_list.JSON", simplejson.dumps(originaltitle_list))
            homewindow.setProperty("title_list.JSON", simplejson.dumps(title_list))
        log("create_light_movielist: " + str(now - time.time()))
    now = time.time()
    for onlineitem in onlinelist:
        found = False
        if onlineitem["Title"].lower() in title_list:
            index = title_list.index(onlineitem["Title"].lower())
            found = True
            # Notify("found title " + onlineitem["Title"])
        elif onlineitem["OriginalTitle"].lower() in originaltitle_list:
            index = originaltitle_list.index(onlineitem["OriginalTitle"].lower())
            found = True
            # Notify("found originaltitle_list " + onlineitem["Title"])
        if found:
            dbid = str(id_list[index])
            # Notify(dbid)
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["streamdetails","year","art","writer","file"], "movieid":%s }, "id": 1}' % dbid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = simplejson.loads(json_query)
            if "moviedetails" in json_response["result"] and "Premiered" in onlineitem:
                # try:
                #     difference = int(onlineitem["Premiered"][:4]) - int(json_response['result']['moviedetails']['year'])
                #     if difference < -2 or difference > 2:
                #         break
                # except:
                #     pass
                response = json_response['result']['moviedetails']
                streaminfo = media_streamdetails(response['file'].encode('utf-8').lower(), response['streamdetails'])
                onlineitem.update({"Play": response["movieid"]})
                onlineitem.update({"DBID": response["movieid"]})
                onlineitem.update({"Path": response['file']})
                onlineitem.update({"FilenameAndPath": response['file']})
                onlineitem.update({"Writer": " / ".join(response['writer'])})
                onlineitem.update({"Logo": response['art'].get("clearlogo", "")})
                onlineitem.update({"DiscArt": response['art'].get("discart", "")})
                onlineitem.update({"Banner": response['art'].get("banner", "")})
                onlineitem.update({"Poster": response['art'].get("poster", "")})
                onlineitem.update({"Thumb": response['art'].get("poster", "")})
                onlineitem.update({"VideoCodec": streaminfo["videocodec"]})
                onlineitem.update({"VideoResolution": streaminfo["videoresolution"]})
                onlineitem.update({"VideoAspect": streaminfo["videoaspect"]})
                onlineitem.update({"AudioCodec": streaminfo["audiocodec"]})
                onlineitem.update({"AudioChannels": str(streaminfo["audiochannels"])})
                audio = response['streamdetails']['audio']
                subtitles = response['streamdetails']['subtitle']
                count = 1
                streams = []
                for item in audio:
                    if item['language'] not in streams:
                        streams.append(item['language'])
                        onlineitem.update({'AudioLanguage.%d' % count: item['language']})
                        onlineitem.update({'AudioCodec.%d' % count: item['codec']})
                        onlineitem.update({'AudioChannels.%d' % count: str(item['channels'])})
                        count += 1
                count = 1
                subs = []
                for item in subtitles:
                    if item['language'] not in subtitles:
                        subs.append(item['language'])
                        onlineitem.update({'SubtitleLanguage.%d' % count: item['language']})
                        count += 1
                onlineitem.update({'SubtitleLanguage': " / ".join(subs)})
                onlineitem.update({'AudioLanguage': " / ".join(streams)})
    log("compare time: " + str(now - time.time()))
    return onlinelist


def GetMusicBrainzIdFromNet(artist, xbmc_artist_id=-1):
    base_url = "http://musicbrainz.org/ws/2/artist/?fmt=json"
    url = '&query=artist:%s' % urllib.quote_plus(artist)
    results = Get_JSON_response(base_url + url, 30)
    if results and len(results["artists"]) > 0:
        mbid = results["artists"][0]["id"]
        log("found artist id for " + artist.decode("utf-8") + ": " + mbid)
        return mbid
    else:
        return None


def CompareAlbumWithLibrary(onlinelist):
    locallist = GetXBMCAlbums()
    for onlineitem in onlinelist:
        for localitem in locallist:
            if onlineitem["name"] == localitem["title"]:
                json_query = xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbumDetails", "params": {"properties": ["thumbnail"], "albumid":%s }, "id": 1}' % str(localitem["albumid"]))
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                json_query = simplejson.loads(json_query)
                album = json_query["result"]["albumdetails"]
                onlineitem.update({"DBID": album["albumid"]})
                onlineitem.update(
                    {"Path": 'XBMC.RunScript(service.skin.widgets,albumid=' + str(album["albumid"]) + ')'})
                if album["thumbnail"]:
                    onlineitem.update({"thumb": album["thumbnail"]})
                    onlineitem.update({"Icon": album["thumbnail"]})
                break
    return onlinelist


def GetStringFromUrl(url):
    succeed = 0
    while (succeed < 5) and (not xbmc.abortRequested):
        try:
            request = urllib2.Request(url)
            request.add_header('User-agent', 'XBMC/13.2 ( ptemming@gmx.net )')
            response = urllib2.urlopen(request)
            data = response.read()
            return data
        except:
            log("GetStringFromURL: could not get data from %s" % url)
            xbmc.sleep(1000)
            succeed += 1
    return None


def Get_JSON_response(url="", cache_days=7.0):
    now = time.time()
    hashed_url = hashlib.md5(url).hexdigest()
    path = xbmc.translatePath(os.path.join(Addon_Data_Path, hashed_url + ".txt"))
    cache_seconds = int(cache_days * 86400.0)
    prop_time = homewindow.getProperty(hashed_url + "_timestamp")
    if prop_time:
        if now - float(prop_time) < cache_seconds:
            prop = simplejson.loads(homewindow.getProperty(hashed_url))
            log("prop load. time: " + str(time.time() - now))
            return prop
    elif xbmcvfs.exists(path) and ((now - os.path.getmtime(path)) < cache_seconds):
        results = read_from_file(path)
    else:
        response = GetStringFromUrl(url)
        try:
            results = simplejson.loads(response)
            log("save to file: " + url)
            save_to_file(results, hashed_url, Addon_Data_Path)
        except:
            log("Exception: Could not get new JSON data. Tryin to fallback to cache")
            log(response)
            if xbmcvfs.exists(path):
                results = read_from_file(path)
            else:
                results = []
    log("file load. time: " + str(time.time() - now))
    homewindow.setProperty(hashed_url + "_timestamp", str(now))
    homewindow.setProperty(hashed_url, simplejson.dumps(results))
    return results


class Get_File(threading.Thread):

    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        cachedthumb = xbmc.getCacheThumbName(self.url)
        xbmc_cache_file = os.path.join(xbmc.translatePath("special://profile/Thumbnails/Video"), cachedthumb[0], cachedthumb)
        if xbmcvfs.exists(xbmc_cache_file):
            log("Cached Image: " + self.url)
            return xbmc_cache_file
        else:
            try:
                log("Download: " + self.url)
                request = urllib2.Request(self.url)
                request.add_header('Accept-encoding', 'gzip')
                response = urllib2.urlopen(request)
                data = response.read()
                response.close()
                log('image downloaded')
            except:
                log('image download failed')
                return ""
            if data != '':
                try:
                    tmpfile = open(xbmc_cache_file, 'wb')
                    tmpfile.write(data)
                    tmpfile.close()
                    return xbmc_cache_file
                except:
                    log('failed to save image')
                    return ""
            else:
                return ""


def GetFavouriteswithType(favtype):
    favs = GetFavourites()
    favlist = []
    for fav in favs:
        if fav["Type"] == favtype:
            favlist.append(fav)
    return favlist


def GetFavPath(fav):
    if fav["type"] == "media":
        path = "PlayMedia(%s)" % (fav["path"])
    elif fav["type"] == "script":
        path = "RunScript(%s)" % (fav["path"])
    else:
        path = "ActivateWindow(%s,%s)" % (
            fav["window"], fav["windowparameter"])
    return path


def GetFavourites():
    items = []
    json_query = xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "Favourites.GetFavourites", "params": {"type": null, "properties": ["path", "thumbnail", "window", "windowparameter"]}, "id": 1}')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = simplejson.loads(json_query)
    if json_query["result"]["limits"]["total"] > 0:
        for fav in json_query["result"]["favourites"]:
            path = GetFavPath(fav)
            newitem = {'Label': fav["title"],
                       'Thumb': fav["thumbnail"],
                       'Type': fav["type"],
                       'Builtin': path,
                       'Path': "plugin://script.extendedinfo/?info=action&&id=" + path}
            items.append(newitem)
    return items


def GetIconPanel(number):
    items = []
    offset = number * 5 - 5
    for i in range(1, 6):
        newitem = {'Label': xbmc.getInfoLabel("Skin.String(IconPanelItem" + str(i + offset) + ".Label)").decode("utf-8"),
                   'Path': "plugin://script.extendedinfo/?info=action&&id=" + xbmc.getInfoLabel("Skin.String(IconPanelItem" + str(i + offset) + ".Path)").decode("utf-8"),
                   'Thumb': xbmc.getInfoLabel("Skin.String(IconPanelItem" + str(i + offset) + ".Icon)").decode("utf-8"),
                   'ID': "IconPanelitem" + str(i + offset).decode("utf-8"),
                   'Type': xbmc.getInfoLabel("Skin.String(IconPanelItem" + str(i + offset) + ".Type)").decode("utf-8")}
        items.append(newitem)
    return items


def GetWeatherImages():
    items = []
    for i in range(1, 6):
        newitem = {'Label': "bla",
                   'Path': "plugin://script.extendedinfo/?info=action&&id=SetFocus(22222)",
                   'Thumb': xbmc.getInfoLabel("Window(weather).Property(Map." + str(i) + ".Area)"),
                   'Layer': xbmc.getInfoLabel("Window(weather).Property(Map." + str(i) + ".Layer)"),
                   'Legend': xbmc.getInfoLabel("Window(weather).Property(Map." + str(i) + ".Legend)")}
        items.append(newitem)
    return items


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def get_browse_dialog(default="", heading="Browse", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False):
    dialog = xbmcgui.Dialog()
    value = dialog.browse(
        dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default)
    return value


def save_to_file(content, filename, path=""):
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
    if 'youtube.com/v' in string:
        vid_ids = re.findall(
            'http://www.youtube.com/v/(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            convertedstring = 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % id
            return convertedstring
    if 'youtube.com/watch' in string:
        vid_ids = re.findall(
            'youtube.com/watch\?v=(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            convertedstring = 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % id
            return convertedstring
    return ""


def ExtractYoutubeID(string):
    if 'youtube.com/v' in string:
        vid_ids = re.findall(
            'http://www.youtube.com/v/(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            return id
    if 'youtube.com/watch' in string:
        vid_ids = re.findall(
            'youtube.com/watch\?v=(.{11})\??', string, re.DOTALL)
        for id in vid_ids:
            return id
    return ""


def Notify(header="", message="", icon=__addonicon__, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    dialog.notification(heading=header, message=message, icon=icon, time=time, sound=sound)


def GetMovieSetName(dbid):
    json_query = xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["setid"], "movieid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if "moviedetails" in json_response["result"]:
        dbsetid = json_response['result']['moviedetails'].get('setid', "")
        if dbsetid:
            json_query = xbmc.executeJSONRPC(
                '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid":%s }, "id": 1}' % dbsetid)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_response = simplejson.loads(json_query)
            return json_response['result']['setdetails'].get('label', "")
    return ""


def prettyprint(string):
    log(simplejson.dumps(
        string, sort_keys=True, indent=4, separators=(',', ': ')))


def GetImdbID(type, dbid):
    if type == "movie":
        json_query = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["imdbnumber","title", "year"], "movieid":%s }, "id": 1}' % dbid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if "moviedetails" in json_response["result"]:
            return json_response['result']['moviedetails']['imdbnumber']
        else:
            return []
    elif type == "tvshow":
        json_query = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShowDetails", "params": {"properties": ["imdbnumber","title", "year"], "tvshowid":%s }, "id": 1}' % dbid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        if "tvshowdetails" in json_response["result"]:
            return json_response['result']['tvshowdetails']['imdbnumber']
        else:
            return []


def GetImdbIDfromEpisode(dbid):
    json_query = xbmc.executeJSONRPC(
        '{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["tvshowid"], "episodeid":%s }, "id": 1}' % dbid)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)
    if "episodedetails" in json_response["result"]:
        tvshowid = str(json_response['result']['episodedetails']['tvshowid'])
        return GetImdbID("tvshow", tvshowid)


def passHomeDataToSkin(data=None, prefix="", debug=False, precache=False):
    if data is not None:
        threads = []
        image_requests = []
        for (key, value) in data.iteritems():
            value = unicode(value)
            if precache:
                if value.startswith("http://") and (value.endswith(".jpg") or value.endswith(".png")):
                    if not value in image_requests and value:
                        thread = Get_File(value)
                        threads += [thread]
                        thread.start()
                        image_requests.append(value)
            homewindow.setProperty('%s%s' % (prefix, str(key)), value)
            if debug:
                log('%s%s' % (prefix, str(key)) + value)
        for x in threads:
            x.join()


def passDataToSkin(name="", data=None, prefix="", controlwindow=None, controlnumber=None, handle=None, limit=False, debug=False):
    if limit and data:
        if limit < len(data):
            data = data[:limit]
    if controlnumber is "plugin":
        homewindow.clearProperty(name)
        if data is not None:
            homewindow.setProperty(name + ".Count", str(len(data)))
            items = CreateListItems(data)
            xbmcplugin.setContent(handle, 'url')
            itemlist = list()
            for item in items:
                itemlist.append((item.getProperty("path"), item, False))
            xbmcplugin.addDirectoryItems(handle, itemlist, False)
    elif controlnumber is not None:
        log("creatin listitems for list with id " + str(controlnumber))
        xbmc.sleep(200)
        itemlist = controlwindow.getControl(controlnumber)
        items = CreateListItems(data)
        itemlist.addItems(items)
    else:
        SetWindowProperties(name, data, prefix, debug)


def SetWindowProperties(name, data, prefix="", debug=False):
    if data is not None:
       # log( "%s%s.Count = %s" % (prefix, name, str(len(data)) ) )
        for (count, result) in enumerate(data):
            if debug:
                log("%s%s.%i = %s" % (prefix, name, count + 1, str(result)))
            for (key, value) in result.iteritems():
                value = unicode(value)
                homewindow.setProperty('%s%s.%i.%s' % (prefix, name, count + 1, str(key)), value)
                if debug:
                    log('%s%s.%i.%s --> ' % (prefix, name, count + 1, str(key)) + value)
        homewindow.setProperty('%s%s.Count' % (prefix, name), str(len(data)))
    else:
        homewindow.setProperty('%s%s.Count' % (prefix, name), '0')
        log("%s%s.Count = None" % (prefix, name))


def CreateListItems(data=None, preload_images=0):
    Int_InfoLabels = ["year", "episode", "season", "top250", "tracknumber", "playcount", "overlay"]
    Float_InfoLabels = ["rating"]
    String_InfoLabels = ["genre", "director", "mpaa", "plot", "plotoutline", "title", "originaltitle", "sorttitle", "duration", "studio", "tagline", "writer",
                         "tvshowtitle", "premiered", "status", "code", "aired", "credits", "lastplayed", "album", "votes", "trailer", "dateadded"]
    itemlist = []
    if data is not None:
        threads = []
        image_requests = []
        for (count, result) in enumerate(data):
            listitem = xbmcgui.ListItem('%s' % (str(count)))
            itempath = ""
            counter = 1
            for (key, value) in result.iteritems():
                value = unicode(value)
                if counter <= preload_images:
                    if value.startswith("http://") and (value.endswith(".jpg") or value.endswith(".png")):
                        if not value in image_requests:
                            thread = Get_File(value)
                            threads += [thread]
                            thread.start()
                            image_requests.append(value)
                if key.lower() in ["name", "label", "title"]:
                    listitem.setLabel(value)
                if key.lower() in ["thumb"]:
                    listitem.setThumbnailImage(value)
                if key.lower() in ["icon"]:
                    listitem.setIconImage(value)
                if key.lower() in ["thumb", "poster", "banner", "fanart", "clearart", "clearlogo", "landscape", "discart", "characterart", "tvshow.fanart", "tvshow.poster", "tvshow.banner", "tvshow.clearart", "tvshow.characterart"]:
                    listitem.setArt({key.lower(): value})
                if key.lower() in ["path"]:
                    itempath = value
           #     log("key: " + unicode(key) + "  value: " + unicode(value))
                if key.lower() in Int_InfoLabels:
                    try:
                        listitem.setInfo('video', {key.lower(): int(value)})
                    except:
                        pass
                if key.lower() in String_InfoLabels:
                    listitem.setInfo('video', {key.lower(): value})
                if key.lower() in Float_InfoLabels:
                    try:
                        listitem.setInfo('video', {key.lower(): "%1.1f" % float(value)})
                    except:
                        pass
                listitem.setProperty('%s' % (key), value)
            listitem.setPath(path=itempath)
            itemlist.append(listitem)
            counter += 1
        for x in threads:
            x.join()
    return itemlist

def cleanText(text):
    if text:
        text = re.sub('(From Wikipedia, the free encyclopedia)|(Description above from the Wikipedia.*?Wikipedia)', '', text)
        text = text.replace('<br \/>', '[CR]')
        text = re.sub('<(.|\n|\r)*?>', '', text)
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&gt;', '>')
        text = text.replace('&lt;', '<')
        text = text.replace('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.', '')
        while True:
            s = text[0]
            e = text[-1]
            if s == u'\u200b':
                text = text[1:]
            if e == u'\u200b':
                text = text[:-1]
            if s == " " or e == " ":
                text = text.strip()
            elif s == "." or e == ".":
                text = text.strip(".")
            elif s == "\n" or e == "\n":
                text = text.strip("\n")
            else:
                break
        return text.strip()
    else:
        return ""
