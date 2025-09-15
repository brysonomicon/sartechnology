import sys

sys.path.append("/jetson-inference/data/SearchlightScanner/backend")
from backend.image_processor import AIProcessor
from backend.video_source import CameraManager
from jetson_utils import videoOutput

"""
Test class to ensure the ai processor and camera manager work
"""


def main():
    ai = AIProcessor()
    cam = CameraManager()
    ai.load_model("ssd-mobilenet-v2", 0.5)
    cam.open("/dev/video0")
    output = videoOutput()

    iterations = 0
    segment = True

    while True:
        iterations += 1
        frame = cam.fetch_frame()
        detections = ai.detect_objects(frame, grid_size=(2, 2))
        # print(detections)
        # for detection in detections, print out detection.ClassID
        for detection in detections:
            print(detection.ClassID)
        output.Render(frame)
        # if iterations == 100:
        # segment = False
        # ai.set_confidence(0.99)
        # print("Confidence level set to 0.99")
        # cam.close()


if __name__ == "__main__":
    main()
