from jetson_utils import videoSource
import cv2


class CameraManager:
    """
    Class for managing the camera.
    This class uses videoSource from jetson_utils or falls back to OpenCV.
    """

    def __init__(self, source, width, height):
        self.source = source
        self.cap = None
        self.connected = False

        pipeline = (f"v4l2src device={source} ! video/x-raw,width={width},height={height} ! "
                    f"videoconvert ! video/x-raw,format=BGR ! appsink")
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            print("GStreamer pipeline failed, falling back to direct v4l2")
            self.cap = cv2.VideoCapture(source)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if self.cap.isOpened():
            self.connected = True
        else:
            print(f"Unable to open camera source: {source}")
            self.cap = None

    def read(self):
        if self.is_connected():
            return self.cap.read()
        return False, None

    def change_camera(self, source):
        self.release()
        self.cap = cv2.VideoCapture(source)
        if self.cap.isOpened():
            self.connected = True
        else:
            print(f"Unable to open camera source: {source}")
            self.cap = None
            self.connected = False

    def change_resolution(self, width, height):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capture(self):
        ret, frame = self.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def getFPS(self):
        if self.is_connected():
            return self.cap.get(cv2.CAP_PROP_FPS)
        return 0

    def release(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

    def is_connected(self):
        return self.cap is not None and self.cap.isOpened()
