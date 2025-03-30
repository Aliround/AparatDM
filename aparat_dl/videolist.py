import requests as req
import threading
import re
import pickle
from aparat_dl import Video
from aparat_dl.utils import *
import os


class VideoList():
    '''qualities : 1080p, 720p, 480p, 360p, 240p, 144p'''
    def __init__(self, dest:str=default_path, quality:str='720p', name:str='Untitled'):
        self.Videos = []
        self.quality = quality
        self.dest = dest
        self.name = name
        self.save = False
    
    def add_url(self, link:str):
        created_videos = []
        if 'https://www.aparat.com/' in link:
            if '/v/' in link:
                link = re.sub(r'[?]playlist.+','',link)
                if not self.is_duplicate(link):
                    video = Video(link, self.quality, self.dest)
                    video.fetch_download_link()
                    self.Videos.append(video)
                    created_videos.append(video)
                else:
                    print('Video exists')
            
            elif '/playlist/' in link:
                created_videos.extend(self.fetch_playlist(link))
            
            elif len(link.replace('https://www.aparat.com/', '')) > 3:
                created_videos.extend(self.fetch_channel(link.split('/')[-1], 0))
            self.save_videos()
        else:
            print('link is invalid!!!')
        return created_videos
       
    def fetch_playlist(self, url:str):
        created_videos = []
        if url.split('/')[-1].isnumeric():
            playlist_id = url.split('/')[-1]
            print(f'Getting playlist --->  {url}')
            req_pl = f"https://www.aparat.com/api/fa/v1/video/playlist/one/playlist_id/{playlist_id}"
            data = req.get(req_pl).json()
            if self.name == 'Untitled':
                self.name = data['data']['attributes']['title']
            self.playlist = data['data']['attributes']['title']
            
            def get_data(vid):
                try:
                    title = format_filename(vid["attributes"]["title"])
                    link = "https://www.aparat.com/v/" + vid["attributes"]['frame'].split('/')[-3]
                    if not self.is_duplicate(link):
                        playlist = format_filename(self.playlist)
                        video = Video(link, self.quality, os.path.join(self.dest, playlist))
                        video.playlist = playlist
                        video.fetch_download_link()
                        self.Videos.append(video)
                        created_videos.append(video)
                    else:
                        print('Video exists')
                except Exception as e:
                    pass
            threads = []
            for vid in data["included"]:
                thread = threading.Thread(target=get_data, args=(vid,))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
        else:
            print('playlist link is invalid!!!')
        return created_videos

    def fetch_channel(self, UserID: str, vid_cnt = 0):
        created_videos = []
        if self.name == 'Untitled':
            self.name = UserID
        print('Getting ' + UserID + ' data...')
        if not vid_cnt:
            req_info = f"https://www.aparat.com/etc/api/profile/username/{UserID}"
            info = req.get(req_info).json()
            vid_cnt = info['profile']['video_cnt']
        req_ch = f"https://www.aparat.com/etc/api/videoByUser/username/{UserID}/perpage/{vid_cnt}"
        data = req.get(req_ch).json()
        for vid in data['videobyuser']:
            title = vid["title"]
            link = "https://www.aparat.com/v/" + vid['frame'].split('/')[-3]
            if not self.is_duplicate(link):
                video = Video(link, self.quality, os.path.join(self.dest, UserID))
                video.playlist = UserID
                video.fetch_download_link()
                self.Videos.append(video)
                created_videos.append(video)
            else:
                print('Video exists')
        print(f"{len(data['videobyuser'])} Videos added to list")
        return created_videos

    def fetch_download_links(self):
        print('Getting download links')
        def get_d(vid):
            if not vid.completed:
                vid.fetch_download_link()
        threads = []
        for vid in self.Videos:
            thread = threading.Thread(target=get_d, args=(vid,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.save_videos()
        print('links are ready')
    
    def fetch_mirror_urls(self):
        print('Getting mirror urls')
        def get_m(vid):
            if not vid.completed:
                vid.fetch_mirror_urls()
        threads = []
        for vid in self.Videos:
            thread = threading.Thread(target=get_m, args=(vid,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.save_videos()
        print('mirror urls are ready')

    def start_queue(self):
        if self.save:
            self.save_videos()
        for vid in self.Videos:
            if not vid.completed:
                vid.download()
            self.save_videos()
    
    def start_all(self):
        if self.save:
            self.save_videos()
        for vid in self.Videos:
            if vid.status == 'stop':
                vid.download()
            self.save_videos()
        
    def show(self):
        for i, vid in enumerate(self.Videos):
            print(f'[{i}] ' + vid.link + ' ==> ' + vid.title + (vid.playlist if vid.playlist != None else '') + (' - Downloaded' if vid.completed else ''))
        
    def find_video(self, url:str=None, title:str=None):
        if url:
            for vid in self.Videos:
                if vid.link == url:
                    return vid
        if title:
            return [vid for vid in self.Videos if title in vid.title]
        return None
        
    def is_duplicate(self, url):
        return any(vid.link == url for vid in self.Videos)
    
    def fetch_thumbnails(self):
        for vid in self.Videos:
            vid.get_thumbnail_image()
    
    def save_videos(self):
        data = {
            'quality': self.quality,
            'dest': self.dest,
            'Videos': self.Videos
        }
        if not os.path.exists('data'):
            os.makedirs('data')
        with open('data\\' + self.name + '.pkl', 'wb') as f:
            pickle.dump(data, f)

    def load_videos(self):
        try:
            with open('data\\' + self.name + '.pkl', 'rb') as f:
                data = pickle.load(f)
                self.quality = data['quality']
                self.dest = data['dest']
                self.Videos = data['Videos']
        except:
            pass