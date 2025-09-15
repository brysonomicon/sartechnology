import os
import time
import threading
from queue import Queue

class SoundManager:
    def __init__(self):
        self.sounds = {
            "default": "/home/sar/SearchlightScannerV4/Initial-test/SearchlightScanner-dev/sounds/beep.mp3",
            "powerline": "/home/sar/SearchlightScanner-dev/sounds/Alarm__Missile_Jettison.ogg.mp3"
        }
        self.last_play_time = 0
        self.cooldown = 0

        self.sound_queue = Queue()
        self.thread = threading.Thread(target=self.run, args=())
        self.running = False
    
    def start(self):
        print("Starting sound manager")
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
    
    def run(self):
        while self.running:
            if not self.sound_queue.empty():
                sound = self.sound_queue.get()
                self._play_sound(sound)

            time.sleep(0.1)  # Adjust the sleep time as needed

    def _play_sound(self, sound):
        os.system(f"mpg123 {sound} > /dev/null 2>&1")
        self.last_play_time = time.time()

    def play_sound(self, detections):
        # check if enough time has passed since last sound
        if time.time() - self.last_play_time < self.cooldown:
            return

        # play sound based on detections
        if detections:
            sound = self.sounds["default"]
            self.cooldown = 2
            for detection in detections:
                if detection.label == "powerline":
                    sound = self.sounds["powerline"]
                    self.cooldown = 9
                    break

            self.sound_queue.put(sound)
