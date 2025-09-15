class SharedConfidence:
    def __init__(self):
        self._value = 0
        self._observers = []

    def register_observer(self, observer_callback):
        self._observers.append(observer_callback)

    def notify_observers(self):
        for callback in self._observers:
            callback(self._value)

    def get_value(self):
        return self._value

    def set_value(self, new_value):
        self._value = new_value
        self.notify_observers()
        
# This will be the shared instance
shared_confidence = SharedConfidence()
