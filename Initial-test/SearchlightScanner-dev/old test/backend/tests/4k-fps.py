from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

argv = ["--input-width=1920", "--input-height=1080"]
input = videoSource("/dev/video0", argv=argv)
output = videoOutput()
input.Open()
net = detectNet("ssd-mobilenet-v2", threshold=0.5)

while True:
    img = input.Capture()
    if img is None:
        continue
    print(output.GetFrameRate())
    detections = net.Detect(img, overlay="box,labels,conf")
    output.Render(img)
    if not input.IsStreaming() or not output.IsStreaming():
        break
