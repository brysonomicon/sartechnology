from jetson_inference import detectNet
from jetson_utils import (cudaToNumpy, cudaFromNumpy)
from .scanner_detection import ScannerDetection
from PIL import Image
import tempfile
import os
import os.path
from frontend.shared_labels_controller import shared_labels
import numpy as np
import cv2


class ImageProcessor:
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.net = None

        labels_and_colors = shared_labels.get_init_labels()
        labels = [label for label, _ in labels_and_colors]
        colors = [color for _, color in labels_and_colors]

        temp_label_file = tempfile.NamedTemporaryFile(delete=False)
        temp_color_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            with open(temp_label_file.name, 'w') as f:
                f.write('\n'.join(labels))
            with open(temp_color_file.name, 'w') as f:
                f.write('\n'.join([f"{r} {g} {b}" for (r, g, b) in colors]))

            if self.model_path and os.path.exists(self.model_path):
                print(f"Loading custom model from: {self.model_path}")
                self.net = detectNet(
                    model=self.model_path,
                    labels=temp_label_file.name,
                    colors=temp_color_file.name,
                    input_blob="input_0",
                    output_cvg="scores",
                    output_bbox="boxes",
                    threshold=0.01
                )
            else:
                print("Using built-in ssd-mobilenet-v2 model")
                self.net = detectNet(
                    "ssd-mobilenet-v2",
                    labels=temp_label_file.name,
                    colors=temp_color_file.name,
                    threshold=0.01
                )

            if not hasattr(self.net, 'SetThreshold'):
                print("Warning: detectNet doesn't have SetThreshold method")

        except Exception as e:
            print(f"Error loading model: {e}")
            raise
        finally:
            os.unlink(temp_label_file.name)
            os.unlink(temp_color_file.name)

    def filter_detections(self, detections):
        filtered = []
        for detection in detections:
            label = self.net.GetClassDesc(detection.ClassID)
            threshold = shared_labels.get_threshold(label)
            if detection.Confidence >= threshold:
                filtered.append(detection)
                # print(f"Accepted detection: {label} ({detection.Confidence:.2f} >= {threshold:.2f})")
            else:
                # print(f"Rejected detection: {label} ({detection.Confidence:.2f} < {threshold:.2f})")
                pass
        return filtered

    def detect_and_collect(self, image_segment):
        detections = self.net.Detect(image_segment, overlay="none")
        detections = self.filter_detections(detections)
        return detections

    def detect(self, image, grid_size=None):
        """Handle both numpy arrays and cudaImage inputs"""
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3:  # Color image
                if image.shape[2] == 3:  # BGR format
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cudaFromNumpy(image)
            else:  # Grayscale
                image = cudaFromNumpy(np.stack((image,) * 3, axis=-1))

        try:
            height, width = image.height, image.width
        except AttributeError:
            print("Warning: Could not get image dimensions, using defaults")
            height, width = 512, 512  # Default model input size

        detections = []
        if grid_size is not None:
            grid_h, grid_w = height // grid_size[0], width // grid_size[1]
            image_np = cudaToNumpy(image)
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    segment = image_np[i * grid_h:(i + 1) * grid_h, j * grid_w:(j + 1) * grid_w]
                    segment = cudaFromNumpy(segment)
                    seg_detections = self.net.Detect(segment, overlay="none")
                    for det in seg_detections:
                        det.Left += j * grid_w
                        det.Right += j * grid_w
                        det.Top += i * grid_h
                        det.Bottom += i * grid_h
                    detections.extend(seg_detections)
        else:
            detections = self.net.Detect(image, overlay="none")

        # Filter detections based on category thresholds
        filtered_detections = self.filter_detections(detections)

        self.net.Overlay(image, filtered_detections, overlay="lines,labels,conf")
        return [ScannerDetection(self.net.GetClassDesc(d.ClassID), d.Confidence) for d in filtered_detections]

    def get_label(self, label_id):
        """
        Get the label for a given label ID.
        Args:
            label_id (int): The ID of the label to get.
        Returns:
            str: The label for the given ID.
        """
        return self.net.GetClassDesc(label_id)