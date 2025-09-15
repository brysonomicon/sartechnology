from pyembedded.gps_module.gps import GPS
import threading
import time
import math

from frontend.application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager


class GPSManager:
    """
    Class for managing the GPS device in a separate thread, ensuring coordinates are updated only when valid.
    """

    def __init__(self, interval=1):
        """
        Initializer for the GPSManager.
        """
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.interval = interval
        self.gps_connected = False
        self.gps = None
        port = self.constants_manager.get_constant("gps_name")
        baud_rate = self.constants_manager.get_constant("gps_baud_rate")

        fallback_ports = [port, "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0",
                          "/dev/ttyUSB1", "/dev/serial0", "/dev/serial1"]

        for attempt_port in fallback_ports:
            try:
                self.gps = GPS(port=attempt_port, baud_rate=baud_rate)
                self.gps_connected = True
                print(f"Connected to GPS on {attempt_port}")
                break
            except Exception as e:
                print(f"Failed to connect to GPS on {attempt_port}: {e}")
        if not self.gps_connected:
            print(
                "No GPS device connected. The program will run without GPS functionality."
            )

        self.running = False
        self.thread = None
        self.latest_coords = None
        self.previous_coords = None
        self.latest_bearing = None
        self.latest_altitude = None
        self.latest_speed = None

    def start(self):
        """
        Starts the background thread to periodically obtain GPS coordinates.
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update_coordinates)
            self.thread.start()

    def stop(self):
        """
        Stops the background thread.
        """
        self.running = False
        if self.thread:
            self.thread.join()

    def _update_coordinates(self):
        """
        The method running within the thread to periodically update the coordinates,
        calculate direction, and calculate speed.
        """

        last_update_time = (
            None  # Track the time of the last update for speed calculation
        )

        while self.running:
            if self.gps_connected:
                try:
                    current_time = time.time()
                    new_coords = self.parse_lat_long_from_raw()
                    if new_coords and new_coords != ("N/A", "N/A"):
                        self.previous_coords = self.latest_coords
                        formatted_coords = (
                            round(new_coords[0], 4),
                            round(new_coords[1], 4),
                        )
                        self.latest_coords = formatted_coords
                        print(f"Updated coordinates: {self.latest_coords}")
                        self._update_altitude()

                        if self.previous_coords is not None:
                            direction = self.calculate_bearing(
                                *self.previous_coords, *self.latest_coords
                            )
                            print(f"Direction: {direction} degrees")

                            if last_update_time:
                                distance = self.calculate_distance(
                                    *self.previous_coords, *self.latest_coords
                                )
                                time_interval = current_time - last_update_time
                                speed = self.calculate_speed(distance, time_interval)
                                print(f"Speed: {speed} meters/second")

                        last_update_time = current_time
                except Exception as e:
                    print(f"Unable to get coordinates from GPS: {e}")

            time.sleep(self.interval)

    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dLon = lon2 - lon1
        x = math.sin(dLon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
            lat2
        ) * math.cos(dLon)
        bearing = math.atan2(x, y)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360  # Normalize to 0-360
        self.latest_bearing = round(bearing, 2)
        # return round(bearing, 2)
        return self.latest_bearing

    def _update_altitude(self):
        """
        Parses the raw NMEA data to update the altitude.
        """
        # Directly use the latest raw data
        raw_data = self.gps.get_raw_data()
        if raw_data and raw_data[0] == "$GPGGA":
            parts = raw_data
            if parts[9]:  # Ensure the altitude field is not empty
                try:
                    self.latest_altitude = round(float(parts[9]), 2)
                    print(f"Updated altitude: {self.latest_altitude} ft")
                except ValueError:
                    print("Failed to parse altitude")

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the distance between two points on the Earth using the Haversine formula.
        """
        R = 6371000  # Radius of the Earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
                math.sin(delta_phi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c  # Distance in meters

    def calculate_speed(self, distance, time_interval):
        """
        Calculate the speed given a distance and time interval.
        """
        if time_interval > 0:
            self.latest_speed = round(distance / time_interval, 2)
            return self.latest_speed
        return 0

    def get_coords(self):
        """
        Getter for the latest valid coordinates obtained by the GPS.

        Returns:
            tuple: The latest valid latitude and longitude of the GPS.

        Raises:
            ValueError: If the GPS has not obtained any valid coordinates yet.
        """
        if self.latest_coords is None:
            raise ValueError("GPS has not obtained any valid coordinates yet.")
        return self.latest_coords

    def get_latest_speed(self):
        """
        Getter for the latest speed calculated.

        Returns:
            float: The latest speed in meters per second.
        """
        return self.latest_speed

    def get_latest_altitude(self):
        """
        Getter for the latest altitude updated.

        Returns:
            float: The latest altitude in feet.

        Raises:
            ValueError: If the altitude could not be parsed.
        """
        return self.latest_altitude

    def get_latest_bearing(self):
        """
        Getter for the latest bearing calculated.

        Returns:
            float: The latest bearing in degrees from true north.
        """
        return self.latest_bearing

    def parse_lat_long_from_raw(self):
        """
        Extracts latitude and longitude from the raw NMEA data.
        This method is used to parse the raw data to get lat/lon values.

        :return: tuple of latitude and longitude
        """
        try:
            raw_data = self.gps.get_raw_data()
            if raw_data and raw_data[0] == "$GPGGA":
                lat_raw = raw_data[2]
                lat_dir = raw_data[3]
                lon_raw = raw_data[4]
                lon_dir = raw_data[5]

                if lat_raw and lon_raw and lat_dir and lon_dir:
                    lat_deg = float(lat_raw[:2])
                    lat_min = float(lat_raw[2:])
                    lat = lat_deg + lat_min / 60
                    if lat_dir == 'S':
                        lat = -lat

                    lon_deg = float(lon_raw[:3])
                    lon_min = float(lon_raw[3:])
                    lon = lon_deg + lon_min / 60
                    if lon_dir == 'W':
                        lon = -lon

                    return round(lat, 6), round(lon, 6)
        except Exception as e:
            print(f"[GPSManager] Error parsing lat/lon from raw: {e}")
        return "N/A", "N/A"

