from datetime import datetime

import numpy as np
from PIL import ImageDraw, ImageFont, Image
import piexif
import os

from frontend.application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager
from fractions import Fraction


class ScannerImage:
    custom_font_path = None
    potential_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def __init__(self, image, detections, gps_coords):
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.font_color = eval(self.constants_manager.get_constant("image_font_color"))
        self.font_size = self.constants_manager.get_constant("image_font_size")
        self.image = image
        self.detections = detections
        self.gps_coords = gps_coords
        self.date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        self.exif_bytes = None
        if ScannerImage.custom_font_path is None:
            if os.path.isfile(ScannerImage.potential_font_path):
                ScannerImage.custom_font_path = ScannerImage.potential_font_path

    def _annotate(self):
        if isinstance(self.image, np.ndarray):
            self.image = Image.fromarray(self.image)

        draw = ImageDraw.Draw(self.image)

        if ScannerImage.custom_font_path:
            font = ImageFont.truetype(ScannerImage.custom_font_path, size=self.font_size)
        else:
            font = ImageFont.load_default()

        if self.gps_coords:
            lat_val = self.gps_coords.get("latitude")
            lon_val = self.gps_coords.get("longitude")
            alt_val = self.gps_coords.get("altitude")
            speed_val = self.gps_coords.get("speed_kmh")
            cog_val = self.gps_coords.get("course_deg")

            #  Format the values, if a detection occurs but gps is not connected/still connecting
            #  the image will have N/A for the gps values
            lat = f"{lat_val:.5f}" if lat_val is not None else "N/A"
            lon = f"{lon_val:.5f}" if lon_val is not None else "N/A"
            alt = f"{alt_val:.1f}m" if alt_val is not None else "N/A"
            speed = f"{speed_val:.1f}" if speed_val is not None else "N/A"
            cog = f"{int(cog_val)}" if cog_val is not None else "N/A"

            full_line = (
                f"Lat/Long: {lat} {lon}   ALT: {alt}   "
                f"COG: {cog}°   SPD: {speed} km/h   {self.date_time}"
            )
        else:
            full_line =  f"{self.date_time}    -- No GPS --"

        draw.text((10, 10), full_line, fill=self.font_color, font=font)

    def _set_gps_coords(self):
        if self.gps_coords is None:
            return
        lat = self.gps_coords.get("latitude")
        lon = self.gps_coords.get("longitude")
        alt = self.gps_coords.get("altitude")
        speed = self.gps_coords.get("speed_kmh")
        cog = self.gps_coords.get("course_deg")
        if "exif" in self.image.info:
            exif_dict = piexif.load(self.image.info["exif"])
        else:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = self._convert_to_degrees(abs(lat))
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "N" if lat >= 0 else "S"
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = self._convert_to_degrees(abs(lon))
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "E" if lon >= 0 else "W"

        if alt is not None:
            exif_dict["GPS"][piexif.GPSIFD.GPSAltitudeRef] = 0 if alt >= 0 else 1
            alt_frac = Fraction(alt).limit_denominator(10000)
            exif_dict["GPS"][piexif.GPSIFD.GPSAltitude] = (alt_frac.numerator, alt_frac.denominator)

        if speed is not None:
            knots = speed * 0.539957
            knots_frac = Fraction(knots).limit_denominator(10000)
            exif_dict["GPS"][piexif.GPSIFD.GPSSpeedRef] = b"K"
            exif_dict["GPS"][piexif.GPSIFD.GPSSpeed] = (knots_frac.numerator, knots_frac.denominator)

        if cog is not None:
            cog_frac = Fraction(cog).limit_denominator(10000)
            exif_dict["GPS"][piexif.GPSIFD.GPSImgDirectionRef] = b"T"
            exif_dict["GPS"][piexif.GPSIFD.GPSImgDirection] = (cog_frac.numerator, cog_frac.denominator)

        self.exif_bytes = piexif.dump(exif_dict)

    @staticmethod
    def _convert_to_degrees(value):
        """Convert a decimal degree value to a tuple of degrees, minutes, and seconds."""
        d = int(value)
        md = abs(value - d) * 60
        m = int(md)
        sd = (md - m) * 60
        return ((d, 1), (m, 1), (int(sd), 1))

    def save(self, filename):
        self._annotate()
        self._set_gps_coords()

        if self.exif_bytes:
            self.image.save(filename, exif=self.exif_bytes)
        else:
            self.image.save(filename)
