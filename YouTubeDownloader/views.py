from datetime import timedelta
from math import floor, log, pow

from django.contrib import messages
from django.shortcuts import render
from requests import get

from YouTubeDownloader.forms import DownloadForm
from pytube import YouTube

# Create your views here.

# Youtube V3 API Key
KEY = "AIzaSyCtS3vyrXm6qGN2ks64eEQtjPJeG5I63m0"


# Convert from bytes
def convertsize(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(floor(log(size_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


# Convert long numbers
def humanformat(number):
    units = ['', 'K', 'M', 'B', 'T', 'Q']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k ** magnitude, units[magnitude])


# when click search button
def download_video(request, string=""):
    global video_url
    form = DownloadForm(request.POST or None)
    if form.is_valid():
        video_url = form.cleaned_data.get("url")
        try:
            yt_obj = YouTube(video_url)
            videos = yt_obj.streams.filter(is_dash=False).desc()
            audios = yt_obj.streams.filter(only_audio=True).order_by('abr').desc()
        except Exception as e:
            messages.error(request, e)
            return render(request, 'home.html', {'form': form})

        video_audio_streams = []
        audio_streams = []

        try:
            url = f"https://www.googleapis.com/youtube/v3/videos?id={yt_obj.video_id}&key={KEY}&part=statistics"
            video_stats = get(url).json()
            print(videos)
            video_likes = video_stats["items"][0]["statistics"]["likeCount"]
            video_favs = video_stats["items"][0]["statistics"]["favoriteCount"]
        except:
            video_likes = 0
            # List of video streams dictionaries
            for s in videos:
                video_audio_streams.append({
                    'resolution': s.resolution,
                    'extension': s.mime_type.replace('video/', ''),
                    'file_size': convertsize(s.filesize),
                    'video_url': s.url,
                    'file_name': yt_obj.title + "." + s.mime_type.replace('video/', '')
                })

            # List of audio streams dictionaries
            for s in audios:
                audio_streams.append({
                    'resolution': s.abr,
                    'extension': s.mime_type.replace('audio/', ''),
                    'file_size': convertsize(s.filesize),
                    'video_url': s.url,
                    'file_name': yt_obj.title + "." + s.mime_type.replace('video/', '')
                })

            if yt_obj.rating == None:
                rating = 5
            else:
                rating = yt_obj.rating

            # Full content to render
            print( yt_obj.title)
            context = {
                'form': form,
                'title': yt_obj.title,
                # 'rating': humanformat(int(video_likes)),
                'thumb': yt_obj.thumbnail_url,
                'author_url': yt_obj.channel_url,
                'duration': str(timedelta(seconds=yt_obj.length)),
                'views': humanformat(yt_obj.views) if yt_obj.views >= 100 else yt_obj.views,
                'stream_audio': audio_streams,
                'streams': video_audio_streams
            }
            return render(request, 'home.html', context)

    return render(request, 'home.html', {'form': form})
