# timer.py
from direct.gui.DirectGui import DirectLabel


class GameTimer:
    def __init__(self, base_app, max_time=120):
        self.app = base_app
        self.max_time = max_time
        self.time_left = max_time
        self.is_running = False

        self.label = DirectLabel(
            text=self.get_formatted_time(),
            text_scale=0.06,
            text_fg=(0.2, 1.0, 0.4, 1),
            frameColor=(0, 0, 0, 0),
            pos=(0.65, 0, 0.85),
        )

        self.app.taskMgr.add(self.update_timer, "UpdateTimerTask")

    def start(self, seconds=None):
        if seconds is not None:
            self.max_time = seconds
            self.time_left = seconds
        self.is_running = True

    def stop(self):
        self.is_running = False

    def reset(self):
        self.time_left = self.max_time
        self.label["text"] = self.get_formatted_time()

    def get_time_left(self):
        return max(0, self.time_left)

    def get_formatted_time(self):
        minutes = int(self.time_left) // 60
        seconds = int(self.time_left) % 60
        return f"TIME LEFT {minutes:02d}:{seconds:02d}"

    def update_timer(self, task):
        if self.is_running and self.time_left > 0:
            dt = self.app.clock.getDt()
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.is_running = False

            self.label["text"] = self.get_formatted_time()
        return task.cont