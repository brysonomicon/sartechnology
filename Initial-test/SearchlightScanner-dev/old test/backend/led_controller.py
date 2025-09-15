import serial
import time
import threading

from frontend.application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager


class LEDController:
    def __init__(self):
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.com_port = self.constants_manager.get_constant("led_name")
        self.baud_rate = self.constants_manager.get_constant("led_baud_rate")
        self.flash_event = threading.Event()
        self.flash_duration = self.constants_manager.get_constant("led_light_duration")
        try:
            self.serial = serial.Serial(self.com_port, self.baud_rate, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self._flash_led_worker)
            self.thread.start()
        except Exception as e:
            # print(f"Error: {str(e)}")
            self.serial = None
            self.running = False

    def flash_led(self, duration=1):
        """Sets the duration and triggers the event to flash the LED."""
        if self.serial is None:
            # print("Error: Serial port not open")
            return
        self.flash_duration = duration
        self.flash_event.set()

    def _flash_led_worker(self):
        """Worker thread that waits for the event to flash LED."""
        while self.running:
            self.flash_event.wait()  # Wait until the event is set
            if not self.running:
                break
            try:
                self.serial.write(b"AT+CH1=1")  # Turn LED on
                time.sleep(self.flash_duration)  # Keep LED on for the set duration
                self.serial.write(b"AT+CH1=0")  # Turn LED off
            except Exception as e:
                # print(f"Error: {str(e)}")
                pass
            self.flash_event.clear()  # Clear the event after flashing

    def close(self):
        """Stops the thread and closes the serial port."""
        self.running = False
        self.flash_event.set()  # Trigger the event to unblock the thread if waiting
        if self.thread:
            self.thread.join()
        if self.serial:
            self.serial.close()
