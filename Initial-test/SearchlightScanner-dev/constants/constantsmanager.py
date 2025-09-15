import os
import json


class ConstantsManager:
    """
    Class to manage constants from a JSON file.
    """

    BACKUP_JSON_STRING = """
    {
    "default_confidence_level": 25,
    "default_distance": 1,
    "default_resolution": "1920x1080 pixels",
    "default_segmentation": 16,
    "camera_feeds": ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3","/dev/video4","/dev/video5"],
    "gps_name": "/dev/ttyACM0",
    "gps_baud_rate": 115200,
    "led_name": "/dev/ttyUSB0",
    "led_baud_rate": 9600,
    "led_light_duration": 2,
    "image_save_dir": "",
    "image_save_rate": 2,
    "images_per_rate": 1,
    "images_per_dir": 100,
    "image_font_size": 16,
    "image_font_color": "(255, 0, 0)",
    "notes1": "",
    "notes2": "",
    "path_to_model": "",
    "path_to_labels": "",
    "default_targets": {
        "BACKGROUND": {"color": "(255, 255, 255)", "threshold": "0.1"},
        "vehicle": {"color": "(34, 177, 76)", "threshold": "0.5"},
        "ocean debris": {"color": "(255, 242, 0)", "threshold": "0.6"},
        "person": {"color": "(163, 73, 164)", "threshold": "0.4"},
        "powerline": {"color": "(255, 174, 201)", "threshold": "0.7"},
        "dog": {"color": "(185, 122, 87)", "threshold": "0.5"},
        "ship wake": {"color": "(136, 0, 21)", "threshold": "0.6"},
        "airplane": {"color": "(237, 28, 36)", "threshold": "0.5"},
        "helicopter": {"color": "(0, 162, 232)", "threshold": "0.5"},
        "Persons_Thermal": {"color": "(63, 72, 204)", "threshold": "0.3"},
        "crashed aircraft": {"color": "(255, 127, 39)", "threshold": "0.4"},
        "crashed helicopter": {"color": "(255, 127, 39)", "threshold": "0.4"},
        "Snows tracks": {"color": "(200, 200, 200)", "threshold": "0.5"},
        "bicycle": {"color": "(0, 128, 0)", "threshold": "0.5"},
        "boat": {"color": "(0, 0, 128)", "threshold": "0.5"},
        "bus": {"color": "(255, 165, 0)", "threshold": "0.5"},
        "car": {"color": "(128, 0, 128)", "threshold": "0.5"},
        "motorcycle": {"color": "(128, 128, 0)", "threshold": "0.5"},
        "oil spill": {"color": "(64, 64, 64)", "threshold": "0.6"},
        "people outdoors": {"color": "(0, 255, 255)", "threshold": "0.4"},
        "train": {"color": "(0, 0, 0)", "threshold": "0.5"},
        "truck": {"color": "(139, 69, 19)", "threshold": "0.5"},
        "vessel": {"color": "(100, 149, 237)", "threshold": "0.5"}
    },
    "category_thresholds": {
        "BACKGROUND": 0.1,
        "vehicle": 0.5,
        "ocean debris": 0.6,
        "person": 0.4,
        "powerline": 0.7,
        "dog": 0.5,
        "ship wake": 0.6,
        "airplane": 0.5,
        "helicopter": 0.5,
        "Persons_Thermal": 0.3,
        "crashed aircraft": 0.4,
        "crashed helicopter": 0.4,
        "Snows tracks": 0.5,
        "bicycle": 0.5,
        "boat": 0.5,
        "bus": 0.5,
        "car": 0.5,
        "motorcycle": 0.5,
        "oil spill": 0.6,
        "people outdoors": 0.4,
        "train": 0.5,
        "truck": 0.5,
        "vessel": 0.5
    },
    "selected_targets": {},
    "operator_notes": "",
    "operator_comments": ""
    }
    """

    def __init__(self, filename="settings.json"):
        """
        Initializer for ConstantsManager.

        Args:
            filename (str, optional): The filename of the JSON file. Defaults to "values.json".

        Raises:
            FileNotFoundError: If an error occurred while creating the file (if the file does not exist and trying to make a new one)
        """
        self.filename = filename
        if not os.path.isfile(self.filename):
            try:
                print(
                    f"The file '{self.filename}' does not exist. Creating a new one..."
                )
                with open(self.filename, "w") as file:
                    file.write(self.BACKUP_JSON_STRING)
            except Exception as e:
                raise FileNotFoundError(
                    f"An error occurred while creating the file: {e}"
                )
        self.constants = {}
        self.load_constants()

    def load_constants(self):
        """
        Reads the constants from the JSON file.

        Raises:
            ValueError: If the file is not a valid JSON file
            ValueError: If an error occurred while reading the file
        """
        try:
            with open(self.filename, "r") as file:
                self.constants = json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"The file '{self.filename}' is not a valid JSON file.")
        except Exception as e:
            raise ValueError(f"An error occurred while reading the file: {e}")

    def get_constant(self, key, default=None):
        """
        Gets the value of a constant.

        Args:
            key (str): The key of the constant

        Returns:
            The value of the constant (None if the constant does not exist)

        """
        return self.constants.get(key, default)

    def set_constant(self, key, value):
        """
        Adds or updates a constant in the JSON file.

        Args:
            key (str): The key of the constant
            value (any): The value of the constant

        Raises:
            ValueError: If an error occurred while writing the file
        """
        self.constants[key] = value
        try:
            with open(self.filename, "w") as file:
                json.dump(self.constants, file, indent=4)
        except Exception as e:
            raise ValueError(f"An error occurred while writing the file: {e}")
