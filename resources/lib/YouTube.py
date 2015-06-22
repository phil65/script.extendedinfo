# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from Utils import *

YT_KEY_2 = 'AIzaSyB-BOZ_o09NLVwq_lMskvvj1olDkFI4JK0'
BASE_URL = "https://www.googleapis.com/youtube/v3/"


def handle_youtube_videos(results):
    videos = []
    log("starting handle_youtube_videos")
    for item in results:
            thumb = ""
            if "thumbnails" in item["snippet"]:
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
            try:
                video_id = item["id"]["videoId"]
            except:
                video_id = item["snippet"]["resourceId"]["videoId"]
            video = {'thumb': thumb,
                     'youtube_id': video_id,
                     'Play': 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % video_id,
                     'path': 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % video_id,
                     'Description': item["snippet"]["description"],
                     'title': item["snippet"]["title"],
                     # 'Author': item["author"][0]["name"]["$t"],
                     'Date': item["snippet"]["publishedAt"].replace("T", " ").replace(".000Z", "")[:-3]}
            videos.append(video)
    return videos


def handle_youtube_playlists(results):
    playlists = []
    log("starting handle_youtube_playlists")
    for item in results:
            thumb = ""
            if "thumbnails" in item["snippet"]:
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
            try:
                playlist_id = item["id"]["playlistId"]
            except:
                playlist_id = item["snippet"]["resourceId"]["playlistId"]
            playlist = {'thumb': thumb,
                        'youtube_id': playlist_id,
                        'Play': 'plugin://script.extendedinfo/?info=youtubeplaylist&&id=%s' % playlist_id,
                        'path': 'plugin://script.extendedinfo/?info=youtubeplaylist&&id=%s' % playlist_id,
                        'Description': item["snippet"]["description"],
                        'title': item["snippet"]["title"],
                        # 'Author': item["author"][0]["name"]["$t"],
                        'Date': item["snippet"]["publishedAt"].replace("T", " ").replace(".000Z", "")[:-3]}
            playlists.append(playlist)
    return playlists


def handle_youtube_channels(results):
    channels = []
    log("starting handle_youtube_channels")
    for item in results:
            thumb = ""
            if "thumbnails" in item["snippet"]:
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
            try:
                channel_id = item["id"]["channelId"]
            except:
                channel_id = item["snippet"]["resourceId"]["channelId"]
            channel = {'thumb': thumb,
                        'youtube_id': channel_id,
                        'Play': 'plugin://script.extendedinfo/?info=youtubechannel&&id=%s' % channel_id,
                        'path': 'plugin://script.extendedinfo/?info=youtubechannel&&id=%s' % channel_id,
                        'Description': item["snippet"]["description"],
                        'title': item["snippet"]["title"],
                        # 'Author': item["author"][0]["name"]["$t"],
                        'Date': item["snippet"]["publishedAt"].replace("T", " ").replace(".000Z", "")[:-3]}
            channels.append(channel)
    return channels


def get_youtube_search_videos(search_string="", hd="", orderby="relevance", limit=40, extended=False, item_info=False, page=1, filter_string="", media_type="video"):
    results = []
    if hd and not hd == "false":
        hd_string = "&hd=true"
    else:
        hd_string = ""
    search_string = url_quote(search_string.replace('"', ''))
    url = 'search?part=id%%2Csnippet&type=%s&q=%s&order=%s&%skey=%s%s&maxResults=%i' % (media_type, search_string, orderby, filter_string, YT_KEY_2, hd_string, int(limit))
    results = get_JSON_response(BASE_URL + url, 0.5, "YouTube")
    prettyprint(results)
    if media_type == "video":
        videos = handle_youtube_videos(results["items"])
        if extended:
            video_ids = [item["youtube_id"] for item in videos]
            url = "videos?id=%s&part=contentDetails%%2Cstatistics&key=%s" % (",".join(video_ids), YT_KEY_2)
            ext_results = get_JSON_response(BASE_URL + url, 0.5, "YouTube")
            for i, item in enumerate(videos):
                for ext_item in ext_results["items"]:
                    if item["youtube_id"] == ext_item['id']:
                        item["duration"] = ext_item['contentDetails']['duration'][2:].lower()
                        item["dimension"] = ext_item['contentDetails']['dimension']
                        item["definition"] = ext_item['contentDetails']['definition']
                        item["caption"] = ext_item['contentDetails']['caption']
                        item["viewcount"] = millify(ext_item['statistics']['viewCount'])
                        item["likes"] = ext_item['statistics']['likeCount']
                        item["dislikes"] = ext_item['statistics']['dislikeCount']
                        vote_count = float(int(ext_item['statistics']['likeCount']) + int(ext_item['statistics']['dislikeCount']))
                        if vote_count > 0:
                            item["rating"] = format(float(ext_item['statistics']['likeCount']) / vote_count * 10, '.2f')
                        break
                else:
                    item["duration"] = ""
    elif media_type == "playlist":
        videos = handle_youtube_playlists(results["items"])
    elif media_type == "channel":
        videos = handle_youtube_channels(results["items"])
    if videos:
        if item_info:
            return videos, results["pageInfo"]["resultsPerPage"], results["pageInfo"]["totalResults"]
        else:
            return videos

    else:
        return []


def get_youtube_playlist_videos(playlist_id=""):
    url = 'playlistItems?part=id%%2Csnippet&maxResults=50&playlist_id=%s&key=%s' % (playlist_id, YT_KEY_2)
    results = get_JSON_response(BASE_URL + url, 0.5, "YouTube")
    if results:
        return handle_youtube_videos(results["items"])
    else:
        return []


def get_youtube_user_playlists(username=""):
    url = 'channels?part=contentDetails&forUsername=%s&key=%s' % (username, YT_KEY_2)
    results = get_JSON_response(BASE_URL + url, 30, "YouTube")
    return results["items"][0]["contentDetails"]["relatedPlaylists"]
