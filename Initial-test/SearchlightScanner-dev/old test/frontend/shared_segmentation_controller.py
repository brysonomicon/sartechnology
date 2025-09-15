class SharedSegmentation:
    def __init__(self):
        self._options = {
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
        self._current = self._options[9]

    def get_options(self):
        return self._options

    def get_current(self):
        return self._current

    def set_current(self, new_value):
        print("SharedSegmentation: set_current:", self._options[new_value])
        self._current = self._options[new_value]


# This will be the shared instance
shared_segmentation = SharedSegmentation()
