import sys

sys.path.append("/jetson-inference/data/SearchlightScanner/backend")
from backend.gps_manager import GPSManager
import time


def main():
    gps = GPSManager()
    while True:
        start_time = time.time()
        coords = gps.get_coords()
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Coordinates: {coords}, Time Taken: {time_taken:.6f} seconds")


if __name__ == "__main__":
    main()
