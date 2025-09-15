from ast import literal_eval
from frontend.application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager


def json_to_dict(json_data):
    labels = {}
    for key, value in json_data.items():
        if isinstance(value, str):
            labels[key] = {
                "color": literal_eval(value),
                "threshold": 0.5
            }
        elif isinstance(value, dict):
            labels[key] = {
                "color": literal_eval(value["color"]),
                "threshold": float(value.get("threshold", 0.5))
            }
    return labels


def dict_to_json(dict_data):
    json_data = {}
    for key, value in dict_data.items():
        json_data[key] = {
            "color": str(value["color"]),
            "threshold": str(value["threshold"])
        }
    return json_data


class SharedLabels:
    def __init__(self):
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.selected_labels = {}
        self.observers = []

        self.labels = {
            "BACKGROUND": {"color": (255, 255, 255), "threshold": 0.1},
            "vehicle": {"color": (34, 177, 76), "threshold": 0.5},
            "ocean debris": {"color": (255, 242, 0), "threshold": 0.6},
            "person": {"color": (163, 73, 164), "threshold": 0.4},
            "powerline": {"color": (255, 174, 201), "threshold": 0.7},
            "dog": {"color": (185, 122, 87), "threshold": 0.5},
            "ship wake": {"color": (136, 0, 21), "threshold": 0.6},
            "airplane": {"color": (237, 28, 36), "threshold": 0.5},
            "helicopter": {"color": (0, 162, 232), "threshold": 0.5},
            "Persons_Thermal": {"color": (63, 72, 204), "threshold": 0.3},
            "crashed aircraft": {"color": (255, 127, 39), "threshold": 0.4},
            "crashed helicopter": {"color": (255, 127, 39), "threshold": 0.4},
            "Snows tracks": {"color": (200, 200, 200), "threshold": 0.5},
            "bicycle": {"color": (0, 128, 0), "threshold": 0.5},
            "boat": {"color": (0, 0, 128), "threshold": 0.5},
            "bus": {"color": (255, 165, 0), "threshold": 0.5},
            "car": {"color": (128, 0, 128), "threshold": 0.5},
            "motorcycle": {"color": (128, 128, 0), "threshold": 0.5},
            "oil spill": {"color": (64, 64, 64), "threshold": 0.6},
            "people outdoors": {"color": (0, 255, 255), "threshold": 0.4},
            "train": {"color": (0, 0, 0), "threshold": 0.5},
            "truck": {"color": (139, 69, 19), "threshold": 0.5},
            "vessel": {"color": (100, 149, 237), "threshold": 0.5}
        }

        self.thresholds = self.constants_manager.get_constant("category_thresholds", {})
        for label in self.labels:
            if label in self.thresholds:
                self.labels[label]["threshold"] = self.thresholds[label]

    def add_observer(self, callback):
        """
        Add an observer callback to the list of observers.
        Basically to notify the ui when the threshold is changed
        :param callback: The observer callback function to be added.
        :return: None
        """
        self.observers.append(callback)

    def notify_observers(self, label, threshold):
        """
        Notify observers with threshold changes.
        :param label: The label whose threshold has changed.
        :param threshold: The new threshold value.
        :return: None
        """
        for callback in self.observers:
            callback(label, threshold)

    def get_threshold(self, label):
        # print(f"Getting threshold for {label}: {self.thresholds.get(label, 0.5)}")
        return max(0.1, self.thresholds.get(label, 0.5))

    def set_threshold(self, label, threshold):
        # print(f"Setting threshold for {label} to {threshold}")
        threshold = max(0.1, threshold)
        self.thresholds[label] = threshold
        self.constants_manager.set_constant("category_thresholds", self.thresholds)
        self.notify_observers(label, threshold)

    def get_color(self, label):
        return self.labels.get(label, {}).get("color", (255, 255, 255))

    def get_init_labels(self):
        return [(label, data["color"]) for label, data in self.labels.items()]

    def get_selected_labels(self):
        return self.selected_labels

    def set_selected_labels(self, labels):
        self.selected_labels = labels
        self.constants_manager.set_constant("selected_labels", labels)

    def get_all_labels(self):
        return self.labels


shared_labels = SharedLabels()
