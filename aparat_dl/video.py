import requests as req
from aparat_dl.utils import *


class Video():
    def __init__(self, link:str, quality:str='720p', dest:str=default_path):
        self.title = 'no title'
        self.link = link
        self.quality = quality
        self.dest = dest
        self.id = link.split('/')[-1]
        self.thumb_url = None
        self.thumb_img = None
        self.duration = None
        self.dlinks = {}
        self.playlist = ''
        self.mirror_urls = []
        self.completed = False
        self.progress = 0
        self.size = 0
    
    def fetch_download_link(self):
        req_vid_info = f"https://www.aparat.com/api/fa/v1/video/video/show/videohash/{self.id}?pr=1&mf=1&referer=channel_page"
        response = req.get(req_vid_info).json()
        try:
            title = response["data"]["attributes"]["title"]
            self.title = format_filename(title)
            self.thumb_url = response["data"]["attributes"]["small_poster"]
            self.get_thumbnail_image()  # Ensure thumbnail is fetched
            self.duration = sec_to_time(response["data"]["attributes"]["duration"])

            for src in response["data"]["attributes"]["playerOption"]["multiSRC"]:
                for link in src:
                    if "label" in link:
                        self.dlinks.update({link["label"]: link["src"]})

            # select next lower quality if the selected quality is not available
            if self.quality not in self.dlinks:
                qualities = ['2190p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
                current_quality_index = qualities.index(self.quality)
                for lower_quality in qualities[current_quality_index + 1:]:
                    if lower_quality in self.dlinks:
                        self.quality = lower_quality
                        break
                        
        except Exception as e:
            print('error while getting download links:', e)
    
    def fetch_mirror_urls(self):
        req_vid_info = f"https://www.aparat.com/api/fa/v1/video/video/show/videohash/{self.id}?pr=1&mf=1&referer=channel_page"
        response = req.get(req_vid_info).json()
        try:
            for src in response["data"]["attributes"]["playerOption"]["multiSRC"]:
                for link in src:
                    if "label" in link:
                        if link["label"] == self.quality:
                            self.mirror_urls.append(link["src"])
                            break
        except Exception as e:
            print('error while getting download links:', e)

        self.status = 'stopped'
        self.dl.stop()
    
    def get_thumbnail_image(self):
        self.thumb_img = req.get(self.thumb_url).content

    def __str__(self):
        return f"Title: {self.title}\nLink: {self.link}\nQuality: {self.quality}p\nDestination: {self.dest}\nDuration: {self.duration}\nSize: {self.size}\nProrgress: {self.progress}"
