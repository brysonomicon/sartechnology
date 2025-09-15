from jetson_utils import videoSource, videoOutput, cudaToNumpy
from jetson_inference import detectNet
from image_saver import ImageSaver
from scanner_detection import ScannerDetection
from PIL import Image


labels = {
    "person": 1,
}
ai = detectNet("ssd-mobilenet-v2", threshold=0.5)
image_saver = ImageSaver(
    save_rate=10,
    save_dir="/jetson-inference/data/ScannerImages",
    images_per_rate=3,
    images_per_dir=10,
    labels=labels,
)
output = videoOutput()
image_saver.start()

camera = videoSource("/dev/video0", argv=["--input-width=1920", "--input-height=1080"])
while True:
    image = camera.Capture()
    detections = ai.Detect(image, overlay="box,labels,conf")
    output.Render(image)
    detections = [ScannerDetection("person", 0.5)]
    image_pil = Image.fromarray(cudaToNumpy(image))
    image_saver.add_image(image_pil, detections, (0, 0))
