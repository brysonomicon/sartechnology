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

        # Try MJPEG
        self.cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        ret, frame = self.cap.read()
        if not ret or frame is None or frame.shape[0] < 100:
            print(f"[CameraManager] MJPG failed on {source}, trying YUYV")
            self.cap.release()
            self.cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

        if self.cap.isOpened():
            self.connected = True
            print(f"[CameraManager] Connected to {source}")
        else:
            print(f"[CameraManager] Failed to open {source}")
            self.cap = None

    def read(self):
        if self.is_connected():
            return self.cap.read()
        return False, None

    def is_connected(self):
        return self.cap is not None and self.cap.isOpened()

    def change_camera(self, source):
        self.release()
        self.__init__(source, 1280, 720)

    def change_resolution(self, width, height):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capture(self):
        ret, frame = self.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def getFPS(self):
        return self.cap.get(cv2.CAP_PROP_FPS) if self.is_connected() else 0

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
