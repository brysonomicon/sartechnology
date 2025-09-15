import sys

sys.path.append("/jetson-inference/data/SearchlightScanner/backend")
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from jetson_inference import detectNet
from jetson_utils import videoSource
import time
from backend.image_processor import AIProcessor
from backend.video_source import CameraManager


# Set up the AI model
ai_processor = AIProcessor()
ai_processor.load_model("ssd-mobilenet-v2", 0.5)

# Set up the camera
camera_manager = CameraManager()
camera_manager.open("/dev/video0", argv=["--input-width=1920", "--input-height=1080"])

# Set up the root window
root = tk.Tk()
root.title("Object Detection")
canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()

# Slider for confidence threshold
conf_thresh = tk.IntVar()
slider_frame = ttk.Frame(root)
slider_frame.pack(pady=10)
confidence_label = ttk.Label(slider_frame, text="0.5")
confidence_label.pack(side=tk.LEFT)
ttk.Label(slider_frame, text="Confidence threshold:").pack(side=tk.LEFT, padx=10)
slider = ttk.Scale(
    slider_frame,
    from_=0,
    to=10,
    orient=tk.HORIZONTAL,
    variable=conf_thresh,
    length=300,
    command=lambda value: (
        confidence_label.config(text="{:.1f}".format(float(value) / 10)),
        ai_processor.set_confidence(float(value) / 10),
    ),
)
slider.set(5)  # Initial value
slider.pack(side=tk.LEFT)


# Create buttons for segmentation options
segmentation_options = {
    1: None,
    4: (2, 2),
    9: (3, 3),
    16: (4, 4),
    25: (5, 5),
    32: (4, 8),
    40: (5, 8),
    50: (5, 10),
    60: (6, 10),
    84: (7, 12),
}

segmentation = None


# Function to set segmentation
def set_segmentation(value):
    global segmentation
    segmentation = segmentation_options[value]


segmentation_buttons_frame = ttk.Frame(root)
segmentation_buttons_frame.pack(pady=10)
ttk.Label(segmentation_buttons_frame, text="Segmentation:").pack(side=tk.LEFT, padx=10)
for option in segmentation_options:
    button = ttk.Button(
        segmentation_buttons_frame,
        text=str(option),
        command=lambda value=option: set_segmentation(value),
    )
    button.pack(side=tk.LEFT, padx=5)


def update():
    global segmentation
    start_time = time.time()
    img = camera_manager.fetch_frame()
    detections = ai_processor.detect_objects(img, segmentation)
    render_image(img, detections)
    fps = 1.0 / (time.time() - start_time)
    print("FPS: {:.2f}".format(fps))
    root.after(1, update)


def render_image(img, detections):
    img_rgb = Image.frombytes("RGB", (img.width, img.height), img)
    img_tk = ImageTk.PhotoImage(image=img_rgb)
    canvas.img_tk = img_tk
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    for detection in detections:
        confidence = detection.Confidence
        if confidence >= conf_thresh.get() / 10:
            left = detection.Left
            top = detection.Top
            right = detection.Right
            bottom = detection.Bottom
            classID = detection.ClassID
            canvas.create_rectangle(left, top, right, bottom, outline="red")
            canvas.create_text(
                left, top, text=f"ClassID: {classID}", anchor=tk.NW, fill="white"
            )
            canvas.create_text(
                left,
                top + 30,
                text="Confidence: {:.1f}%".format(confidence * 100),
                anchor=tk.SW,
                fill="white",
            )


update()

root.mainloop()

camera_manager.close()
