import re
from time import sleep

default_path = r"F:\Video\Game\RIP"

def sec_to_time(seconds):
    try:
        hr = int(seconds) // 3600
        min = (int(seconds) % 3600) // 60
        sec = int(seconds) % 60
        return f'{hr:02}:{min:02}:{sec:02}'
    except:
        return "00:00:00"

def format_filename(name:str):
    string = re.sub(r'[<>:"\\/|?*.]', ' ', name)
    newstr = re.sub(r'\s+', ' ', string)
    return(newstr)

class dlder():
    def __init__(self):
        self.progress = 0
        self.completed = False
        self.speed = '20 Mb/s'
        self.size = '450 Mb'
        self.stopped = True

    def start(self):
        self.stopped = False
        while not self.completed and not self.stopped:
            self.progress += 1
            if self.progress == 100:
                self.completed = True
            sleep(0.1)

    def stop(self):
        self.stopped = True