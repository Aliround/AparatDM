from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame
import pyperclip
from aparat_dl import *
from aparat_dl.utils import *
import os
from PIL import Image, ImageTk
from io import BytesIO
from threading import *
from time import sleep
from pypdl import Pypdl
from concurrent.futures import CancelledError


class Vid_box():
    def __init__(self, app:object, video:object):
        self.video = video
        self.dest = video.dest
        self.app = app  # Store app instance
        img_data = video.thumb_img
        img = Image.open(BytesIO(img_data))
        img = img.resize((160, 90), Image.LANCZOS)
        self.thumb = ImageTk.PhotoImage(img)
        self.title = video.title if video.title else "No Title"
        self.duration = video.duration if video.duration else "Unknown"
        self.quality = video.quality
        self.progress = self.video.progress
        self.size = self.video.size
        #! self.video.completed = False
        self.completed = self.video.completed
        self.running = False
        self.queue = False
        self.drawed = False
        self.dl = Pypdl()
        #! self.dl = dlder()
        
    def start(self):
        if not self.running:
            self.running = True
            self.download_thread = Thread(target=self.download)
            self.download_thread.daemon = True
            self.download_thread.start()
            self.app.root.after(100, self.update_tile)
            self.spr_btn.configure(text='Pause', bootstyle='warning-outline', command=self.stop)
        
    def download(self):
        name = self.title + '.mp4'
        url = self.video.dlinks[self.quality]
        try:
            self.dl.start(url, os.path.join(self.dest, name), retries=3, mirrors=self.video.mirror_urls, display=False)
        except CancelledError:
            print("Download was cancelled.")
        self.running = False
        self.queue = False

    def add_to_queue(self):
        self.queue = True
        self.spr_btn.configure(text='Pending', bootstyle='info', command=self.remove_from_queue)
        if not self.app.downloading:
            self.app.start_download()
    
    def remove_from_queue(self):
        self.queue = False
        self.spr_btn.configure(text='Start', bootstyle='success-outline', command=self.add_to_queue)
        
    def stop(self):
        try:
            try:
                self.size = round(self.dl.size / (1024 ** 2), 2)
                self.video.size = self.size
            except:
                self.size = self.video.size
            self.video.progress = self.progress
            self.dl.stop()
            self.spr_btn.configure(text="start", bootstyle='success-outline', command=self.add_to_queue)
            self.running = False
            self.queue = False
        except Exception as e:
            print('stop error:', e)
        
    def delete(self):
        if self.running:
            self.stop()
        elif self.queue:
            self.unque()

        self.app.vl.Videos.remove(self.video)
        self.app.video_list.remove(self)
        for wid in self.app.vlist.winfo_children():
            if wid == self.frame:
                wid.destroy()
        self.app.save()
        
    def update_tile(self):
        try:
            self.eta = self.dl.eta
            self.eta_label.configure(text=f'eta: {sec_to_time(self.eta)}')
            self.completed = self.dl.completed
            self.video.completed = self.completed
            self.progress = self.dl.progress
            self.video.progress = self.progress
            self.prog_label.configure(text = f'{self.progress} %')
            if self.running:
                self.bar['value'] = self.progress
                try:
                    self.speed_lable.configure(text=f'Speed: {round(self.dl.speed, 2)} MB/s')
                    self.size_lable.configure(text=f'Size: {round(self.dl.size / (1024 ** 2), 2)} Mb')
                except Exception as e:
                    # error: unsupported operand type(s) for /: 'NoneType' and 'int'
                    if e.args[0] == "unsupported operand type(s) for /: 'NoneType' and 'int'":
                        self.speed_lable.configure(text=f'Speed: -- MB/s')
                        self.size_lable.configure(text=f'Size: -- Mb')
                    else:
                        print('update_tile error:', e)
                    
                self.app.root.after(100, self.update_tile)
            elif self.completed:
                self.bar['value'] = 100
                self.spr_btn.configure(text='Finished', bootstyle='light', command=None, state='disabled')
                self.queque = False
                self.app.save()
            elif not self.running:
                self.spr_btn.configure(text='Resume', bootstyle='success-outline', command=self.start)
        except Exception as e:
            print('update_tile error:', e)
    
    def draw(self):
        try:
            self.frame = tb.Frame(self.app.vlist, bootstyle = 'dark')
            self.frame.pack(expand=True, fill='x', padx=(5, 15), pady=4)
            if self.thumb:
                thumb_frame = tb.Frame(self.frame)
                thumb_frame.pack(side='left', pady=5, padx=5)
                thumb = tb.Label(thumb_frame, image=self.thumb)
                thumb.pack()
                duration_label = tb.Label(thumb_frame, text=self.duration, background='black', foreground='white')
                duration_label.place(relx=0.15, rely=0.85, anchor=CENTER)
            else:
                thumb = tb.Label(self.frame, text="No Thumbnail")
                thumb.pack(side='left', pady=5, padx=5)
            
            self.info_frame = tb.Frame(self.frame, bootstyle = 'dark')
            self.info_frame.pack(side='left', fill='y', padx=(0,15))
            
            self.title_ui = tb.Label(self.info_frame, text=self.title, background='grey19', wraplength=240, width=40, justify='right')
            self.title_ui.pack(fill='y', anchor="w", expand=True)
            
            self.down_frame = tb.Frame(self.info_frame, bootstyle='dark')
            self.down_frame.pack(expand=True, fill='x')

            self.size_lable = tb.Label(self.down_frame, text=f'Size: {self.size} Mb', background='grey19')
            self.size_lable.pack(side='left', pady=(0, 3), fill='both', expand=True)

            qu_values = ['1080p', '720p', '480p', '360p', '240p', '144p']
            self.quality_box = tb.Combobox(self.down_frame, values=qu_values, width=8, state='readonly', bootstyle='success')
            self.quality_box.current(qu_values.index(self.quality))
            self.quality_box.pack(side='left', padx=5, pady=(0,8), anchor='w', expand=True)
            self.quality_box.bind("<<ComboboxSelected>>", self.update_quality)

            self.path_frame = tb.Frame(self.frame, bootstyle = 'dark')
            self.path_frame.pack(side='left', fill='both', expand=True)
            
            self.path_var = tb.StringVar()
            self.path_var.trace_add('write', lambda *args: self.update_path())
            self.path = tb.Entry(self.path_frame, width=20, bootstyle='success', textvariable=self.path_var)
            self.path.pack(pady=(5), fill='x', expand=True)
            self.path.insert(0, self.dest)
            
            self.bar = tb.Progressbar(self.path_frame, maximum=100, style='success')
            self.bar.pack(pady=(0, 1), fill='both', expand=True)
            self.bar['value'] = self.progress

            self.prog_label = tb.Label(self.bar, text=f'{self.progress} %',)
            self.prog_label.pack(expand=True)
            
            self.speed_frame = tb.Frame(self.path_frame, bootstyle = 'dark')
            self.speed_frame.pack(fill='both', expand=True)
            
            self.speed_lable = tb.Label(self.speed_frame, text='Speed: -- MB/s', background='grey19')
            self.speed_lable.pack(side='left', pady=(0, 3), fill='both', expand=True)

            self.eta_label = tb.Label(self.speed_frame, text='eta: -- s', background='grey19')
            self.eta_label.pack(side='left', pady=(0, 3), fill='both', expand=True)
            
            self.btn_frame = tb.Frame(self.frame, bootstyle = 'dark')
            self.btn_frame.pack(fill='y', expand=True)
            
            if self.completed:
                self.spr_btn = tb.Button(self.btn_frame, text="Finished", width=8, bootstyle= 'light')
                self.spr_btn.pack(padx=10, pady=(15,8))
            else:
                self.spr_btn = tb.Button(self.btn_frame, text="Start", width=8, bootstyle= 'success-outline', command=self.add_to_queue)
                self.spr_btn.pack(padx=10, pady=(15,8))
            
            self.delete_btn = tb.Button(self.btn_frame, text="Delete", width=8, bootstyle= 'danger', command=self.delete)
            self.delete_btn.pack(padx=10, pady=(5,10))
        except Exception as e:
            print(e)

    def update_quality(self, event):
        self.video.quality = self.quality_box.get()
    
    def update_path(self):
        self.video.dest = self.path_var.get()


class App():
    def __init__(self):
        root = tb.Window(themename = 'darkly')
        root.title('Aparat Downloade')
        root.geometry('750x600') 
        root.iconbitmap("Aparat.ico")
        self.root = root
        self.video_list = []
        self.pending_vids = []
        self.recent_value = pyperclip.paste()
        self.downloading = False
        self.vid_list_frame_border = tb.LabelFrame(self.root, bootstyle = 'success')
        self.vlist = ScrolledFrame(self.vid_list_frame_border, autohide=False)
        
    def start_download(self):
        if not self.downloading:
            self.downloading = True
            t3 = Thread(target=self.download_videos)
            t3.daemon = True
            t3.start()
    
    def download_videos(self):
        while self.downloading:
            for vidbox in self.video_list:
                if vidbox.queue:
                    vidbox.start()
                    while vidbox.queue:
                        sleep(0.5)
            if all(not x.queue for x in self.video_list):
                self.downloading = False
        self.downloading = False
        print('download finished')
        
    def draw(self):
        panel = tb.Frame(self.root)
        panel.pack(fill='x')
        self.vid_list_frame_border.pack(expand=True, fill='both', padx=8, pady=(0,8))
        self.vlist.pack(expand=True, fill='both', padx=(0,5))

        ssframe = tb.Frame(panel)
        ssframe.pack(side='left', fill='y')
        start_all_btn = tb.Button(ssframe, text='Start all', bootstyle = 'success-outline', command=self.start_all)
        start_all_btn.pack(padx=10, pady=(10,5))
        stop_all_btn = tb.Button(ssframe, text='Stop all', bootstyle = 'danger-outline', command=self.stop_all)
        stop_all_btn.pack(padx=10, pady=(5,10))

        inp_frame = tb.Frame(panel)
        inp_frame.pack(side='left', fill='both', expand=True)

        path_frame = tb.Frame(inp_frame)
        path_frame.pack(fill='both', expand=True)
        button_frame = tb.Frame(inp_frame)
        button_frame.pack(fill='both', expand=True)

        path_txt = tb.Label(path_frame, text='Path')
        path_txt.pack(side='left', padx=2)
        path_input = tb.Entry(path_frame)
        path_input.pack(side='left', padx=(0, 10), pady=(5,10), expand=True, fill='x')

        clear_all = tb.Button(button_frame, text='Clear all', command=self.clear_all, style='warning-outline')
        clear_all.pack(side='left', padx=10)
        save_btn = tb.Button(button_frame, text='Save', command=self.save)
        save_btn.pack(side='left', padx=10)
        but3 = tb.Button(button_frame, text='button 3')
        but3.pack(side='left', padx=10)
        
        add_frame = tb.Frame(panel)
        add_frame.pack(side='left', fill='y', padx=(0,10))

        qu_values = ['1080p', '720p', '480p', '360p', '240p', '144p']
        self.quality_choose = tb.Combobox(add_frame, values=qu_values, width=8, state='readonly', bootstyle='success')
        self.quality_choose.pack(pady=(10,5))
        self.quality_choose.current(1)

        add_btn = tb.Button(add_frame, text='Add', width=8, bootstyle = 'success')
        add_btn.pack(pady=(5,10))

        get_d_frame = tb.Frame(panel)
        get_d_frame.pack(side='left', fill='both')

        get_dlink_btn = tb.Button(get_d_frame, text="Get download link", style='success-outline', width=16, command=self.get_mirror_link)
        get_dlink_btn.pack(padx=(0,8), pady=10)

        clear_btn = tb.Button(get_d_frame, text="Clear finished", style='success-outline', width=16, command=self.clear_finished)
        clear_btn.pack(padx=(0,8))
    
    def start_all(self):
        for vidbox in self.video_list:
            if not vidbox.completed:
                vidbox.add_to_queue()
        if not self.downloading:
            self.start_download()
            self.downloading=True
    
    def stop_all(self):
        for vidbox in self.video_list:
            try:
                if vidbox.queue and vidbox.running:
                    vidbox.stop()
                if vidbox.queue and not vidbox.running:
                    vidbox.remove_from_queue()
            except:
                vidbox.remove_from_queue()
        self.downloading = False
    
    def clear_finished(self):
        new_list = [vid for vid in self.vl.Videos if not vid.completed]
        self.vl.Videos = new_list
        self.save()
        self.update()
    
    def clear_all(self):
        self.vl.Videos = []
        self.video_list = []
        for widget in self.vlist.winfo_children():
            widget.destroy()
    
    def add_video_box(self, vid_box:object):
        self.video_list.append(vid_box)
        vid_box.draw()

    def load_videos(self):
        try:
            self.vl = VideoList(name='Download_list')
            self.vl.load_videos()
            for vid in self.vl.Videos:
                vid_box = Vid_box(self, vid)
                self.add_video_box(vid_box)
        except Exception as e:
            print(f"loading videos: {e}")
            self.vl = VideoList(name='Download_list')
            self.vl.save = True
            for vid in self.vl.Videos:
                self.add_video_box(Vid_box(self, vid))
    
    def run(self):
        self.draw()
        self.load_videos()
        self.listen_for_clipboard()
        self.root.mainloop()
    
    def get_mirror_link(self):
        self.vl.get_miror_urls()

    def save(self):
        self.vl.save_videos()
    
    def update(self):
        print('updating ui')
        for widget in self.vlist.winfo_children():
            widget.destroy()
        self.load_videos()

    def add_url(self, url):
        new_videos = self.vl.add_url(url)
        for video in new_videos:
            if video.thumb_img is None:
                video.get_thumbnail_image()
            vid_box = Vid_box(self, video)
            self.add_video_box(vid_box)

    def listen_for_clipboard(self):
        tmp_value = pyperclip.paste()
        if (tmp_value != self.recent_value):
            if 'https://www.aparat.com/' in tmp_value:
                self.vl.quality = self.quality_choose.get()
                self.recent_value = tmp_value
                t2 = Thread(target=self.add_url, args=[tmp_value])
                t2.daemon = True
                t2.start()
            else:
                self.recent_value = tmp_value
                toast = ToastNotification(title='Aparat Downloader',
                    message="Copied link is invalid!",
                    duration=6000,
                    alert=True,
                    position=(1600, 20, 'sw'),)
                toast.show_toast()
                print('Copied link is invalid!')
        self.root.after(200, self.listen_for_clipboard)

