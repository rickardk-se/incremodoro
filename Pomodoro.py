import time
import webbrowser


class Pomodoro:
    def __init__(self, timer=25, short_break=5, long_break=15):
        self.timer = timer
        self.short_break = short_break
        self.long_break = long_break

    def review(self, notes, pattern):
        queue = sorted(notes, reverse=True, key=lambda x: x.h_url.split("/")[-2])
        for note in queue:
            if pattern and pattern not in note.title:
                continue
            if len(note.highlight) == 1:
                webbrowser.open(note.ch_url, autoraise=False)
            else:
                webbrowser.open(note.h_url, autoraise=False)
            time.sleep(0.1)
