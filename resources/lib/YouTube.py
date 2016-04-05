# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import Utils
import urllib
import itertools

YT_KEY = 'AIzaSyB-BOZ_o09NLVwq_lMskvvj1olDkFI4JK0'
BASE_URL = "https://www.googleapis.com/youtube/v3/"
PLUGIN_BASE = "plugin://script.extendedinfo/?info="


def handle_videos(results, extended=False):
    videos = []
    for item in results:
        snippet = item["snippet"]
        thumb = snippet["thumbnails"]["high"]["url"] if "thumbnails" in snippet else ""
        try:
            video_id = item["id"]["videoId"]
        except Exception:
            video_id = snippet["resourceId"]["videoId"]
        video = Utils.ListItem(label=snippet["title"],
                               path=PLUGIN_BASE + 'youtubevideo&&id=%s' % video_id)
        video.set_infos({'Plot': snippet["description"],
                         'Premiered': snippet["publishedAt"][:10]})
        video.set_artwork({'thumb': thumb})
        video.set_properties({'channel_title': snippet["channelTitle"],
                              'channel_id': snippet["channelId"],
                              'youtube_id': video_id,
                              'Play': PLUGIN_BASE + 'youtubevideo&&id=%s' % video_id})
        videos.append(video)
    if not extended:
        return videos
    params = {"part": "contentDetails,statistics",
              "id": ",".join([i.get_property("youtube_id") for i in videos])}
    ext_results = get_data(method="videos",
                           params=params)
    if not ext_results:
        return videos
    for item in videos:
        for ext_item in ext_results["items"]:
            if not item.get_property("youtube_id") == ext_item['id']:
                continue
            duration = ext_item['contentDetails']['duration'][2:-1].split("M")
            likes = ext_item['statistics'].get('likeCount')
            dislikes = ext_item['statistics'].get('dislikeCount')
            item.set_info("duration", int(duration[0]) * 60 + int(duration[1]) if len(duration) > 1 else "")
            props = {"duration": ext_item['contentDetails']['duration'][2:].lower(),
                     "dimension": ext_item['contentDetails']['dimension'],
                     "definition": ext_item['contentDetails']['definition'],
                     "caption": ext_item['contentDetails']['caption'],
                     "viewcount": Utils.millify(ext_item['statistics']['viewCount']),
                     "likes": likes,
                     "dislikes": dislikes}
            item.update_properties(props)
            if likes and dislikes:
                vote_count = int(likes) + int(dislikes)
                if vote_count > 0:
                    item.set_info("rating", format(float(likes) / vote_count * 10, '.2f'))
            break
    return videos


def handle_playlists(results):
    playlists = []
    for item in results:
        snippet = item["snippet"]
        thumb = snippet["thumbnails"]["high"]["url"] if "thumbnails" in snippet else ""
        try:
            playlist_id = item["id"]["playlistId"]
        except Exception:
            playlist_id = snippet["resourceId"]["playlistId"]
        playlist = {'path': PLUGIN_BASE + 'youtubeplaylist&&id=%s' % playlist_id,
                    'label': snippet["title"]}
        playlist["infos"] = {'Plot': snippet["description"],
                             'Premiered': snippet["publishedAt"][:10]}
        playlist["artwork"] = {'thumb': thumb}
        playlist["properties"] = {'youtube_id': playlist_id,
                                  'Play': PLUGIN_BASE + 'youtubeplaylist&&id=%s' % playlist_id,
                                  'channel_title': snippet["channelTitle"],
                                  'live': snippet["liveBroadcastContent"].replace("none", "")}
        playlists.append(playlist)
    params = {"id": ",".join([i["properties"]["youtube_id"] for i in playlists]),
              "part": "contentDetails"}
    ext_results = get_data(method="playlists",
                           params=params)
    for item, ext_item in itertools.product(playlists, ext_results["items"]):
        if item["properties"]["youtube_id"] == ext_item['id']:
            item["properties"]["itemcount"] = ext_item['contentDetails']['itemCount']
    return playlists


def handle_channels(results):
    channels = []
    for item in results:
        snippet = item["snippet"]
        thumb = snippet["thumbnails"]["high"]["url"] if "thumbnails" in snippet else ""
        try:
            channel_id = item["id"]["channelId"]
        except Exception:
            channel_id = snippet["resourceId"]["channelId"]
        channel = {'path': PLUGIN_BASE + 'youtubechannel&&id=%s' % channel_id,
                   'label': snippet["title"]}
        channel["infos"] = {'Plot': snippet["description"],
                            'Premiered': snippet["publishedAt"][:10]}
        channel["artwork"] = {'thumb': thumb}
        channel["properties"] = {'youtube_id': channel_id,
                                 'Play': PLUGIN_BASE + 'youtubechannel&&id=%s' % channel_id}
        channels.append(channel)
    channel_ids = [item["properties"]["youtube_id"] for item in channels]
    params = {"id": ",".join(channel_ids),
              "part": "contentDetails,statistics,brandingSettings"}
    ext_results = get_data(method="channels",
                           params=params)
    for item, ext_item in itertools.product(channels, ext_results["items"]):
        if item["properties"]["youtube_id"] == ext_item['id']:
            item["properties"]["itemcount"] = ext_item['statistics']['videoCount']
            item["artwork"]["fanart"] = ext_item["brandingSettings"]["image"].get("bannerTvMediumImageUrl", "")
    return channels


def get_data(method, params=None, cache_days=0.5):
    params = params if params else {}
    params["key"] = YT_KEY
    params = {k: v for k, v in params.items() if v}
    params = {k: unicode(v).encode('utf-8') for k, v in params.items()}
    url = "{base_url}{method}?{params}".format(base_url=BASE_URL,
                                               method=method,
                                               params=urllib.urlencode(params))
    return Utils.get_JSON_response(url=url,
                                   cache_days=cache_days,
                                   folder="YouTube")


def search(search_str="", hd="", orderby="relevance", limit=40, extended=True, page="", filters=None, media_type="video"):
    params = {"part": "id,snippet",
              "maxResults": limit,
              "type": media_type,
              "order": orderby,
              "pageToken": page,
              "hd": str(hd and not hd == "false"),
              "q": search_str.replace('"', '')}
    params = Utils.merge_dicts(params, filters if filters else {})
    results = get_data(method="search",
                       params=params)
    if not results:
        return {}
    if media_type == "video":
        listitems = handle_videos(results["items"], extended=extended)
    elif media_type == "playlist":
        listitems = handle_playlists(results["items"])
    elif media_type == "channel":
        listitems = handle_channels(results["items"])
    if not listitems:
        return {}
    return {"listitems": listitems,
            "results_per_page": results["pageInfo"]["resultsPerPage"],
            "total_results": results["pageInfo"]["totalResults"],
            "next_page_token": results.get("nextPageToken", ""),
            "prev_page_token": results.get("prevPageToken", "")}


def get_playlist_videos(playlist_id=""):
    if not playlist_id:
        return []
    params = {"part": "id,snippet",
              "maxResults": "50",
              "playlistId": playlist_id}
    results = get_data(method="playlistItems",
                       params=params)
    if not results:
        return []
    return handle_videos(results["items"])


def get_user_playlists(username=""):
    params = {"part": "contentDetails",
              "forUsername": username}
    results = get_data(method="channels",
                       params=params)
    if not results["items"]:
        return None
    return results["items"][0]["contentDetails"]["relatedPlaylists"]
