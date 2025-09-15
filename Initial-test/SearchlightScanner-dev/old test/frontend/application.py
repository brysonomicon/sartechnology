from pathlib import Path

from .application_color_scheme import color_scheme
from .camera_frame import MainFrame
from .settings1 import SettingsFrame1
from .settings2 import SettingsFrame2
import tkinter as tk
import cv2
from backend.video_source import CameraManager
import platform
from backend.image_processor import ImageProcessor
from backend.gps_manager import GPSManager
from .application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager


def get_resolution(pixels):
    dimensions = pixels.split()
    width_height_str = dimensions[0].split("x")
    width = int(width_height_str[0])
    height = int(width_height_str[1])
    return (width, height)


class CameraFeed:
    def __init__(self, video_source=0):
        self.set_video_source(video_source)

    def set_video_source(self, video_source):
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()

        self.video_source = video_source
        self.cap = cv2.VideoCapture(video_source)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def release(self):
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.model_path = self.resolve_model_path()
        self.ai = ImageProcessor(model_path=self.model_path)
        self.color_scheme = color_scheme
        self.title("SearchLightScanner")
        self.update_colors()

        self.bind("<Escape>", self.minimize_window)
        self.set_window_size()

        width, height = get_resolution(
            self.constants_manager.get_constant("default_resolution")
        )
        self.camera_feed_1 = CameraManager(
            source=self.constants_manager.get_constant("camera_feed_1"),
            width=width,
            height=height,
        )
        self.camera_feed_2 = CameraManager(
            source=self.constants_manager.get_constant("camera_feed_2"),
            width=width,
            height=height,
        )
        self.gps_manager = GPSManager()

        self.frames = {}
        for F in (MainFrame, SettingsFrame1, SettingsFrame2):
            if F == MainFrame:
                frame = F(self, self.gps_manager, self.camera_feed_1, self.camera_feed_2, self.color_scheme)
                self.main_frame = frame
            elif F == SettingsFrame1:
                frame = F(self, self.camera_feed_1, self.camera_feed_2, self, self.color_scheme)
            else:
                frame = F(self, self.color_scheme)
            self.frames[F] = frame
            frame.pack(fill="both", expand=True)

        self.switch_frame(MainFrame)
        self.maximize_window()

    def update_colors(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]
        self.configure(bg=color_scheme["application/window_and_frame_color"])

    def quit_application(self):
        self.on_close()

    def toggle_dark_mode(self):
        self.color_scheme["dark_mode"] = not self.color_scheme["dark_mode"]
        self.update_colors()
        for frame in self.frames.values():
            frame.update_colors()

    def switch_frame(self, frame_class):
        for frame in self.frames.values():
            frame.pack_forget()

        frame = self.frames[frame_class]
        frame.pack(fill="both", expand=True)

        if frame_class == MainFrame:
            frame.start_camera_feed()
        else:
            self.frames[MainFrame].stop_camera_feed()

    def switch_settings1(self):
        self.switch_frame(SettingsFrame1)

    def switch_settings2(self):
        self.switch_frame(SettingsFrame2)

    def switch_main_frame(self):
        self.switch_frame(MainFrame)

    def maximize_window(self):
        if platform.system() == "Linux":
            self.attributes("-fullscreen", True)
        elif platform.system() == "Windows":
            self.state("zoomed")
        else:
            self.geometry(
                "{0}x{1}+0+0".format(
                    self.winfo_screenwidth(), self.winfo_screenheight()
                )
            )

    def minimize_window(self, event=None):
        self.iconify()

    def on_close(self):
        if hasattr(self, "gps_manager"):
            self.gps_manager.stop()
        self.frames[MainFrame].stop_camera_feed()
        self.camera_feed_1.release()
        self.camera_feed_2.release()
        self.frames[MainFrame].sound_manager.stop()
        self.frames[MainFrame].saver.stop()
        self.destroy()

    def set_window_size(self):
        self.geometry("1920x969")
        self.resizable(True, True)
        self.minsize(1280, 720)

    def resolve_model_path(self):
        custom_model = Path(
            "/home/sar/SearchlightScannerV4/Initial-test/SearchlightScanner-dev/models/ssd-mobilenet.onnx")
        if custom_model.exists():
            print(f"✅ Using model at: {custom_model}")
            return str(custom_model)

        raise FileNotFoundError(f"❌ Model not found at: {custom_model}")


if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
