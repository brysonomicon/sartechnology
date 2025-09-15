class SharedAlert:
    def __init__(self):
        self._value = False

    def get_value(self):
        return self._value

    def set_value(self, new_value):
        self._value = new_value
        print('SharedAlert: set_value:', self._value)

# This will be the shared instance
shared_alert = SharedAlert()