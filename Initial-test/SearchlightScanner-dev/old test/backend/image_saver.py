import threading
import queue
import time
import os
from .scanner_image import ScannerImage
from frontend.shared_labels_controller import shared_labels
from frontend.application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager


class ImageSaver:
    priority_mapping = {
        1: 1.00,
        2: 0.95,
        3: 0.90,
        4: 0.80,
        5: 0.70,
        6: 0.60,
    }

    def __init__(self, labels):
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.save_rate = self.constants_manager.get_constant("image_save_rate")
        self.save_dir = self.constants_manager.get_constant("image_save_dir")
        self.images_per_rate = self.constants_manager.get_constant("images_per_rate")
        self.images_per_dir = self.constants_manager.get_constant("images_per_dir")
        self.labels = labels
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.run, args=())
        # self.thread.daemon = True
        self.running = False

    def start(self):
        print("Starting image saver")
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def update_labels(self, labels):
        self.labels = labels

    def add_image(self, image, detections, gps_coords):
        image_copy = image.copy()
        self.queue.put(ScannerImage(image_copy, detections, gps_coords))

    def run(self):
        while self.running:
            try:
                print("Processing queue")
                self.process_queue()
                time.sleep(self.save_rate)
            except queue.Empty:
                print("Queue is empty")
                continue

    def process_queue(self):
        images = self.collect_and_sort_images()
        self.save_images(images)

    def collect_and_sort_images(self):
        self.labels = shared_labels.get_selected_labels()
        print(f"Selected labels: {self.labels}")
        print(f"Collecting {self.queue.qsize()} images")
        images = []
        while not self.queue.empty():
            scanner_image = self.queue.get()
            score = self.assign_priority_scores(scanner_image)
            images.append((score, scanner_image))
        images.sort(key=lambda x: x[0], reverse=True)
        images = [image[1] for image in images][: self.images_per_rate]
        images.sort(key=lambda x: x.date_time)
        return images

    def assign_priority_scores(self, scanner_image):
        score = 0
        for detection in scanner_image.detections:
            priority = self.labels.get(detection.label, 1)
            multiplier = self.priority_mapping.get(priority, 1)
            score += detection.conf * multiplier
        return score

    def save_images(self, images):
        print(f"Saving {len(images)} images")
        current_dir = 0
        base_dir = self.save_dir
        current_dir_path = os.path.join(base_dir, f"DET{current_dir}")
        if not os.path.exists(current_dir_path):
            os.makedirs(current_dir_path, exist_ok=True)
        else:
            while os.path.exists(current_dir_path):
                current_dir_files = len(os.listdir(current_dir_path))
                if current_dir_files + len(images) > self.images_per_dir:
                    current_dir += 1
                    current_dir_path = os.path.join(base_dir, f"DET{current_dir}")
                else:
                    break
            os.makedirs(current_dir_path, exist_ok=True)

        last_image_number = len(os.listdir(current_dir_path))

        for i, scanner_image in enumerate(images, start=last_image_number + 1):
            image_name = f"DET_{scanner_image.date_time}"
            image_path = os.path.join(current_dir_path, f"{image_name}.jpg")
            scanner_image.save(image_path)

