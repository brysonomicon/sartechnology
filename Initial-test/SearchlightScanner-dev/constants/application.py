import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser

from constants.constantsmanager import ConstantsManager

segmentation_options = [
    {
        "text": "1 segments",
        "value": 1,
    },
    {
        "text": "4 segments",
        "value": 4,
    },
    {
        "text": "9 segments",
        "value": 9,
    },
    {
        "text": "16 segments",
        "value": 16,
    },
    {
        "text": "25 segments",
        "value": 25,
    },
    {
        "text": "40 segments",
        "value": 40,
    },
    {
        "text": "50 segments",
        "value": 60,
    },
    {
        "text": "84 segments",
        "value": 84,
    },
]

resolution_options = [
    {
        "text": "280x720 pixels",
        "value": "280x720 pixels",
    },
    {
        "text": "1920x1080 pixels",
        "value": "1920x1080 pixels",
    },
    {
        "text": "2560x1440 pixels",
        "value": "2560x1440 pixels",
    },
    {
        "text": "3840x2160 pixels",
        "value": "3840x2160 pixels",
    },
]


def get_segmentation_value(text):
    for option in segmentation_options:
        if option["text"] == text:
            return option["value"]
    return None  # Return None if text is not found


def get_resolution_value(text):
    for option in resolution_options:
        if option["text"] == text:
            return option["value"]
    return None  # Return None if text is not found


def rgb_to_hex(rgb_color_string):
    # Extract RGB values from the string
    rgb_values = tuple(map(int, rgb_color_string.strip("()").split(", ")))

    # Convert RGB values to hexadecimal format
    hex_color = "#%02x%02x%02x" % rgb_values

    return hex_color


def read_csv_and_convert_to_json(csv_file_path):
    data = {}
    try:
        with open(csv_file_path, newline="") as csvfile:
            for line in csvfile:
                category, r, g, b = line.strip().split(",")
                data[category] = str((int(r), int(g), int(b)))
    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
    return data


def is_decimal(string):
    # Check if the string has only one decimal point and all characters are digits
    return string.replace(".", "", 1).isdigit() and string.count(".") <= 1


def is_incomplete_decimal(string):
    # Check if the string is empty
    if not string:
        return True
    elif str.isdigit(string):
        return True
    # Check if the string ends with a decimal point
    elif string.endswith("."):
        return True
    # Check if the string has a decimal point but no digits after it
    elif "." in string and not string.rstrip("0").endswith("."):
        return True
    else:
        return False


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Constants")
        self.configure(bg="#7C889C")
        self.geometry("663x700")

        # Create a Main Frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create a Canvas
        self.my_canvas = tk.Canvas(main_frame)
        self.my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add a Scrollbar to the Canvas
        my_scrollbar = ttk.Scrollbar(
            main_frame, orient=tk.VERTICAL, command=self.my_canvas.yview
        )
        my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the Canvas
        self.my_canvas.configure(yscrollcommand=my_scrollbar.set)
        self.my_canvas.bind(
            "<Configure>",
            lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all")),
        )

        self.constants_manager = ConstantsManager()

        # Instance variables to store values
        # scanning constants
        self.default_confidence_level = tk.IntVar(
            value=int(self.constants_manager.get_constant("default_confidence_level"))
        )
        self.default_distance = tk.IntVar(
            value=int(self.constants_manager.get_constant("default_distance"))
        )
        self.default_resolution = tk.StringVar(
            value=self.constants_manager.get_constant("default_resolution")
        )
        self.default_segmentation = tk.StringVar(
            value=str(self.constants_manager.get_constant("default_segmentation"))
            + " segments"
        )
        self.camera_feed_1 = tk.StringVar(
            value=str(self.constants_manager.get_constant("camera_feed_1"))
        )
        self.camera_feed_2 = tk.StringVar(
            value=str(self.constants_manager.get_constant("camera_feed_2"))
        )

        # gps constants
        self.gps_name = tk.StringVar(
            value=str(self.constants_manager.get_constant("gps_name"))
        )
        self.gps_baud_rate = tk.IntVar(
            value=int(self.constants_manager.get_constant("gps_baud_rate"))
        )

        # led constants
        self.led_name = tk.StringVar(
            value=str(self.constants_manager.get_constant("led_name"))
        )
        self.led_baud_rate = tk.IntVar(
            value=int(self.constants_manager.get_constant("led_baud_rate"))
        )
        self.led_light_duration = tk.DoubleVar(
            value=float(self.constants_manager.get_constant("led_light_duration"))
        )

        # image save constants
        self.image_save_dir = tk.StringVar(
            value=str(self.constants_manager.get_constant("image_save_dir"))
        )
        self.image_save_rate = tk.DoubleVar(
            value=float(self.constants_manager.get_constant("image_save_rate"))
        )
        self.images_per_rate = tk.IntVar(
            value=int(self.constants_manager.get_constant("images_per_rate"))
        )
        self.images_per_directory = tk.IntVar(
            value=int(self.constants_manager.get_constant("images_per_dir"))
        )
        self.image_font_size = tk.IntVar(
            value=int(self.constants_manager.get_constant("image_font_size"))
        )
        self.image_font_color = tk.StringVar(
            value=str(self.constants_manager.get_constant("image_font_color"))
        )
        self.image_font_color.trace("w", self.update_image_font_color)

        # notes
        self.notes1 = tk.StringVar(value=self.constants_manager.get_constant("notes1"))
        self.notes2 = tk.StringVar(value=self.constants_manager.get_constant("notes2"))

        # paths
        self.default_model_path = tk.StringVar(
            value=self.constants_manager.get_constant("path_to_model")
        )
        self.default_labels_path = tk.StringVar(
            value=self.constants_manager.get_constant("path_to_labels")
        )

        self.create_form()

    def on_close(self):
        self.destroy()

    def browse_image_save_dir(self):
        image_save_dir_path = filedialog.askdirectory()
        if image_save_dir_path:
            self.image_save_dir.set(image_save_dir_path)

    def browse_font_color(self):
        color_code = colorchooser.askcolor(title="Choose Color")
        if color_code[0] is not None:
            rgb_color_code, _ = color_code
            self.image_font_color.set(str(rgb_color_code))

    def browse_model(self):
        model_path = filedialog.askopenfilename(
            filetypes=[("ONYX files", "*.onyx"), ("All files", "*.*")]
        )
        if model_path:
            self.default_model_path.set(model_path)

    def browse_labels(self):
        labels_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if labels_path:
            self.default_labels_path.set(labels_path)

    def validate_numeric_input(self, P):
        if str.isdigit(P) or P == "":
            return True
        else:
            return False

    def validate_decimal_input(self, P):
        if is_decimal(P) or P == "":
            return True
        else:
            return False

    def update_confidence_level(self, event):
        value = self.confidence_level_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value > 100 or int_value < 0:
                self.confidence_level_entry.delete(0, tk.END)
            else:
                self.default_confidence_level.set(int_value)
        else:
            self.confidence_level_entry.delete(0, tk.END)

    def update_distance(self, event):
        value = self.default_distance_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value > 100:
                self.default_distance_entry.delete(0, tk.END)
            self.default_distance.set(int(value))
        else:
            self.default_distance_entry.delete(0, tk.END)

    def update_segmentation(self, event):
        self.default_segmentation.set(self.segmentation_entry.get())

    def update_resolution(self, event):
        self.default_resolution.set(self.resolution_entry.get())

    def update_camera_feed_1(self, event):
        self.camera_feed_1.set(self.camera_feed_1_entry.get())

    def update_camera_feed_2(self, event):
        self.camera_feed_2.set(self.camera_feed_2_entry.get())

    def update_gps_name(self, event):
        self.gps_name.set(self.gps_name_entry.get())

    def update_gps_baud_rate(self, event):
        value = self.gps_baud_rate_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value < 0:
                self.gps_baud_rate_entry.delete(0, tk.END)
            self.gps_baud_rate.set(int(value))
        else:
            self.gps_baud_rate_entry.delete(0, tk.END)

    def update_image_save_rate(self, event):
        value = self.image_save_rate_entry.get()
        if is_incomplete_decimal(value):
            return
        if self.validate_decimal_input(value):
            float_value = float(value)
            if float_value < 0.1 or float_value > 86400:
                self.image_save_rate_entry.delete(0, tk.END)
            self.image_save_rate.set(float(value))
        else:
            self.image_save_rate_entry.delete(0, tk.END)

    def update_images_per_rate(self, event):
        value = self.images_per_rate_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value < 0:
                self.images_per_rate_entry.delete(0, tk.END)
            self.images_per_rate.set(int(value))
        else:
            self.images_per_rate_entry.delete(0, tk.END)

    def update_images_per_directory(self, event):
        value = self.images_per_directory_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value < 0:
                self.images_per_directory_entry.delete(0, tk.END)
            self.images_per_directory.set(int(value))
        else:
            self.images_per_directory_entry.delete(0, tk.END)

    def update_image_font_size(self, event):
        value = self.image_font_size_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value < 0:
                self.image_font_size_entry.delete(0, tk.END)
            self.image_font_size.set(int(value))
        else:
            self.image_font_size_entry.delete(0, tk.END)

    def update_image_font_color(self, *args):
        rgb_color_string = self.image_font_color.get()
        hex_color = rgb_to_hex(rgb_color_string)
        self.image_font_color_box.config(bg=hex_color)

    def update_led_name(self, event):
        self.led_name.set(self.led_name_entry.get())

    def update_led_baud_rate(self, event):
        value = self.led_baud_rate_entry.get()
        if self.validate_numeric_input(value):
            int_value = int(value)
            if int_value < 0:
                self.led_baud_rate_entry.delete(0, tk.END)
            self.led_baud_rate.set(int(value))
        else:
            self.led_baud_rate_entry.delete(0, tk.END)

    def update_led_light_duration(self, event):
        value = self.led_light_duration_entry.get()
        print(value)
        print(is_incomplete_decimal(value))
        if is_incomplete_decimal(value):
            return
        if self.validate_decimal_input(value):
            float_value = float(value)
            if float_value < 0.1 or float_value > 86400:
                self.led_light_duration_entry.delete(0, tk.END)
            self.led_light_duration.set(float(value))
        else:
            self.led_light_duration_entry.delete(0, tk.END)

    def update_notes1(self, event):
        self.notes1.set(self.notes1_entry.get("1.0", "end-1c"))

    def update_notes2(self, event):
        self.notes2.set(self.notes2_entry.get("1.0", "end-1c"))

    def save_constants(self):
        default_targets = read_csv_and_convert_to_json(self.default_labels_path.get())

        self.constants_manager.set_constant(
            "default_confidence_level", self.default_confidence_level.get()
        )
        self.constants_manager.set_constant(
            "default_distance", self.default_distance.get()
        )
        self.constants_manager.set_constant(
            "default_resolution", get_resolution_value(self.default_resolution.get())
        )
        self.constants_manager.set_constant(
            "default_segmentation",
            get_segmentation_value(self.default_segmentation.get()),
        )
        self.constants_manager.set_constant("camera_feed_1", self.camera_feed_1.get())
        self.constants_manager.set_constant("camera_feed_2", self.camera_feed_2.get())
        self.constants_manager.set_constant("gps_name", self.gps_name.get())
        self.constants_manager.set_constant("gps_baud_rate", self.gps_baud_rate.get())
        self.constants_manager.set_constant("led_name", self.led_name.get())
        self.constants_manager.set_constant("led_baud_rate", self.led_baud_rate.get())
        self.constants_manager.set_constant(
            "led_light_duration", self.led_light_duration.get()
        )
        self.constants_manager.set_constant("image_save_dir", self.image_save_dir.get())
        self.constants_manager.set_constant(
            "image_save_rate", self.image_save_rate.get()
        )
        self.constants_manager.set_constant(
            "images_per_rate", self.images_per_rate.get()
        )
        self.constants_manager.set_constant(
            "images_per_dir", self.images_per_directory.get()
        )
        self.constants_manager.set_constant(
            "image_font_size", self.image_font_size.get()
        )
        self.constants_manager.set_constant(
            "image_font_color", self.image_font_color.get()
        )
        self.constants_manager.set_constant("notes1", self.notes1.get())
        self.constants_manager.set_constant("notes2", self.notes2.get())
        self.constants_manager.set_constant(
            "path_to_model", self.default_model_path.get()
        )
        self.constants_manager.set_constant(
            "path_to_labels", self.default_labels_path.get()
        )
        self.constants_manager.set_constant("default_targets", default_targets)

        messagebox.showinfo("Success", "Constants saved successfully!")
        print("Constants saved successfully!")

    def create_form(self):
        form_frame = tk.Frame(self.my_canvas, bg="#7C889C")
        self.my_canvas.create_window((0, 0), window=form_frame, anchor="nw")

        row = 0
        root_label = tk.Label(
            form_frame,
            text="Searchlight Scanner Constants",
            font=("Arial", 14, "bold"),
            bg="#7C889C",
            fg="white",
        )
        root_label.grid(row=row, columnspan=2, pady=(10, 25), sticky="w")
        row += 1

        # form_frame = tk.Frame(self, bg="#7C889C")
        # form_frame.pack(pady=(0, 10))

        # Scanning Constants Header
        scanning_constants_header = tk.Label(
            form_frame,
            text="Scanning Constants",
            font=("Arial", 10, "bold"),
            bg="#7C889C",
            fg="white",
        )
        scanning_constants_header.grid(row=row, columnspan=2, pady=(20, 5), sticky="w")
        row += 1

        # Default Confidence Level
        confidence_level_label = tk.Label(
            form_frame, text="Default confidence level (25%):", bg="#7C889C", fg="white"
        )
        confidence_level_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.confidence_level_entry = tk.Entry(
            form_frame, textvariable=self.default_confidence_level
        )
        self.confidence_level_entry.grid(row=row, column=1, padx=10, pady=5)
        self.confidence_level_entry.bind("<KeyRelease>", self.update_confidence_level)
        self.confidence_level_entry.config(validate="key")
        self.confidence_level_entry["validatecommand"] = (
            self.confidence_level_entry.register(self.validate_numeric_input),
            "%P",
        )
        row += 1

        # Defult distance
        distance_label = tk.Label(
            form_frame,
            text="Default distance/focal length (pixels):",
            bg="#7C889C",
            fg="white",
        )
        distance_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.default_distance_entry = tk.Entry(
            form_frame, textvariable=self.default_distance
        )
        self.default_distance_entry.grid(row=row, column=1, padx=10, pady=5)
        self.confidence_level_entry.bind("<KeyRelease>", self.update_distance)
        self.default_distance_entry.config(validate="key")
        self.default_distance_entry["validatecommand"] = (
            self.default_distance_entry.register(self.validate_numeric_input),
            "%P",
        )
        row += 1

        # Default Resolution
        resolution_label = tk.Label(
            form_frame, text="Default resolution (1920x1080):", bg="#7C889C", fg="white"
        )
        resolution_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.resolution_entry = ttk.Combobox(
            form_frame,
            values=[option["text"] for option in resolution_options],
            textvariable=self.default_resolution,
        )
        self.resolution_entry.grid(row=row, column=1, padx=10, pady=5)
        self.resolution_entry.bind("<<ComboboxSelected>>", self.update_resolution)
        row += 1

        # Default Segmentation (Single-select)
        segmentation_label = tk.Label(
            form_frame,
            text="Default segmentation (9 segments):",
            bg="#7C889C",
            fg="white",
        )
        segmentation_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.segmentation_entry = ttk.Combobox(
            form_frame,
            values=[option["text"] for option in segmentation_options],
            textvariable=self.default_segmentation,
        )
        self.segmentation_entry.grid(row=row, column=1, padx=10, pady=5)
        self.segmentation_entry.bind("<<ComboboxSelected>>", self.update_segmentation)
        row += 1

        # Camera Feed 1
        camera_feed_1_label = tk.Label(
            form_frame,
            text="Camera Feed 1:",
            bg="#7C889C",
            fg="white",
        )
        camera_feed_1_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.camera_feed_1_entry = tk.Entry(form_frame, textvariable=self.camera_feed_1)
        self.camera_feed_1_entry.grid(row=row, column=1, padx=10, pady=5)
        self.camera_feed_1_entry.bind("<KeyRelease>", self.update_camera_feed_1)
        self.camera_feed_1_entry.config(validate="key")
        row += 1

        # Camera Feed 2
        camera_feed_2_label = tk.Label(
            form_frame,
            text="Camera Feed 2:",
            bg="#7C889C",
            fg="white",
        )
        camera_feed_2_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.camera_feed_2_entry = tk.Entry(form_frame, textvariable=self.camera_feed_2)
        self.camera_feed_2_entry.grid(row=row, column=1, padx=10, pady=5)
        self.camera_feed_2_entry.bind("<KeyRelease>", self.update_camera_feed_2)
        self.camera_feed_2_entry.config(validate="key")
        row += 1

        # GPS Constants Header
        gps_constants_header = tk.Label(
            form_frame,
            text="GPS Constants",
            font=("Arial", 10, "bold"),
            bg="#7C889C",
            fg="white",
        )
        gps_constants_header.grid(row=row, columnspan=2, pady=(20, 5), sticky="w")
        row += 1

        # GPS Name
        gps_name_label = tk.Label(form_frame, text="GPS Name", bg="#7C889C", fg="white")
        gps_name_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.gps_name_entry = tk.Entry(form_frame, textvariable=self.gps_name)
        self.gps_name_entry.grid(row=row, column=1, padx=10, pady=5)
        self.gps_name_entry.bind("<KeyRelease>", self.update_gps_name)
        self.gps_name_entry.config(validate="key")
        row += 1

        # GPS Baud Rate
        gps_baud_rate_label = tk.Label(
            form_frame,
            text="GPS Baud Rate:",
            bg="#7C889C",
            fg="white",
        )
        gps_baud_rate_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.gps_baud_rate_entry = tk.Entry(form_frame, textvariable=self.gps_baud_rate)
        self.gps_baud_rate_entry.grid(row=row, column=1, padx=10, pady=5)
        self.gps_baud_rate_entry.bind("<KeyRelease>", self.update_gps_baud_rate)
        self.gps_baud_rate_entry.config(validate="key")
        self.gps_baud_rate_entry["validatecommand"] = (
            self.gps_baud_rate_entry.register(self.validate_numeric_input),
            "%P",
        )
        row += 1

        # LED Constants Header
        led_constants_header = tk.Label(
            form_frame,
            text="LED Constants",
            font=("Arial", 10, "bold"),
            bg="#7C889C",
            fg="white",
        )
        led_constants_header.grid(row=row, columnspan=2, pady=(20, 5), sticky="w")
        row += 1

        # LED Name
        led_name_label = tk.Label(form_frame, text="LED Name", bg="#7C889C", fg="white")
        led_name_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.led_name_entry = tk.Entry(form_frame, textvariable=self.led_name)
        self.led_name_entry.grid(row=row, column=1, padx=10, pady=5)
        self.led_name_entry.bind("<KeyRelease>", self.update_led_name)
        self.led_name_entry.config(validate="key")
        row += 1

        # LED Baud Rate
        led_baud_rate_label = tk.Label(
            form_frame,
            text="LED Baud Rate:",
            bg="#7C889C",
            fg="white",
        )
        led_baud_rate_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.led_baud_rate_entry = tk.Entry(form_frame, textvariable=self.led_baud_rate)
        self.led_baud_rate_entry.grid(row=row, column=1, padx=10, pady=5)
        self.led_baud_rate_entry.bind("<KeyRelease>", self.update_led_baud_rate)
        self.led_baud_rate_entry.config(validate="key")
        row += 1

        # LED Light Duration
        led_light_duration_label = tk.Label(
            form_frame,
            text="LED Light Duration (seconds):",
            bg="#7C889C",
            fg="white",
        )
        led_light_duration_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.led_light_duration_entry = tk.Entry(
            form_frame, textvariable=self.led_light_duration
        )
        self.led_light_duration_entry.grid(row=row, column=1, padx=10, pady=5)
        self.led_light_duration_entry.bind(
            "<KeyRelease>", self.update_led_light_duration
        )
        self.led_light_duration_entry.config(validate="key")
        row += 1

        # Image Save Constants Header
        image_save_constants_header = tk.Label(
            form_frame,
            text="Image Save Constants",
            font=("Arial", 10, "bold"),
            bg="#7C889C",
            fg="white",
        )
        image_save_constants_header.grid(
            row=row, columnspan=2, pady=(20, 5), sticky="w"
        )
        row += 1

        # Image Save Directory
        image_frame = tk.Frame(form_frame, bg="#7C889C")
        image_frame.grid(row=row, columnspan=2, pady=(10, 5))

        image_save_dir_label = tk.Label(
            image_frame, text="Image save directory:", bg="#7C889C", fg="white"
        )
        image_save_dir_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.image_save_dir_entry = tk.Entry(
            image_frame, width=30, textvariable=self.image_save_dir
        )
        self.image_save_dir_entry.grid(row=0, column=1, padx=10, pady=5)
        browse_image_save_dir_button = tk.Button(
            image_frame, text="Browse", command=self.browse_image_save_dir
        )
        browse_image_save_dir_button.grid(row=0, column=2, padx=5, pady=5)
        row += 1

        # Image Save Rate
        image_save_rate_label = tk.Label(
            form_frame,
            text="Image Save Rate (seconds):",
            bg="#7C889C",
            fg="white",
        )
        image_save_rate_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.image_save_rate_entry = tk.Entry(
            form_frame, textvariable=self.image_save_rate
        )
        self.image_save_rate_entry.grid(row=row, column=1, padx=10, pady=5)
        self.image_save_rate_entry.bind("<KeyRelease>", self.update_image_save_rate)
        self.image_save_rate_entry.config(validate="key")
        row += 1

        # Images Per Rate
        images_per_rate_label = tk.Label(
            form_frame,
            text="Images Per Rate:",
            bg="#7C889C",
            fg="white",
        )
        images_per_rate_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.images_per_rate_entry = tk.Entry(
            form_frame, textvariable=self.images_per_rate
        )
        self.images_per_rate_entry.grid(row=row, column=1, padx=10, pady=5)
        self.images_per_rate_entry.bind("<KeyRelease>", self.update_images_per_rate)
        self.images_per_rate_entry.config(validate="key")
        row += 1

        # Images Per Directory
        images_per_directory_label = tk.Label(
            form_frame,
            text="Images Per Directory:",
            bg="#7C889C",
            fg="white",
        )
        images_per_directory_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.images_per_directory_entry = tk.Entry(
            form_frame, textvariable=self.images_per_directory
        )
        self.images_per_directory_entry.grid(row=row, column=1, padx=10, pady=5)
        self.images_per_directory_entry.bind(
            "<KeyRelease>", self.update_images_per_directory
        )
        self.images_per_directory_entry.config(validate="key")
        row += 1

        # Image Font Size
        image_font_size_label = tk.Label(
            form_frame,
            text="Image Font Size:",
            bg="#7C889C",
            fg="white",
        )
        image_font_size_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.image_font_size_entry = tk.Entry(
            form_frame, textvariable=self.image_font_size
        )
        self.image_font_size_entry.grid(row=row, column=1, padx=10, pady=5)
        self.image_font_size_entry.bind("<KeyRelease>", self.update_image_font_size)
        self.image_font_size_entry.config(validate="key")
        row += 1

        # Image Font Color
        image_font_color_frame = tk.Frame(form_frame, bg="#7C889C")
        image_font_color_frame.grid(row=row, columnspan=2, pady=(5, 10))

        image_font_color_label = tk.Label(
            image_font_color_frame,
            text="Image Font Color:",
            bg="#7C889C",
            fg="white",
        )
        image_font_color_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.image_font_color_box = tk.Label(
            image_font_color_frame,
            width=4,
            height=1,
            bg=rgb_to_hex(self.image_font_color.get()),
        )
        self.image_font_color_box.grid(row=0, column=1, padx=10, pady=5)
        choose_image_font_color_button = tk.Button(
            image_font_color_frame, text="Choose Color", command=self.browse_font_color
        )
        choose_image_font_color_button.grid(row=0, column=2, padx=5, pady=5)
        row += 1

        # Notes Header
        notes_header = tk.Label(
            form_frame,
            text="Notes",
            font=("Arial", 10, "bold"),
            bg="#7C889C",
            fg="white",
        )
        notes_header.grid(row=row, columnspan=2, pady=(20, 5), sticky="w")
        row += 1

        # Notes 1
        notes1_label = tk.Label(
            form_frame, text="Constants notes 1:", bg="#7C889C", fg="white"
        )
        notes1_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.notes1_entry = tk.Text(form_frame, height=5, width=50)
        self.notes1_entry.insert("1.0", self.notes1.get())
        self.notes1_entry.grid(row=row, column=1, padx=10, pady=5, columnspan=2)
        self.notes1_entry.bind("<KeyRelease>", self.update_notes1)
        row += 1

        # Notes 2
        notes2_label = tk.Label(
            form_frame, text="Constants notes 2:", bg="#7C889C", fg="white"
        )
        notes2_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.notes2_entry = tk.Text(form_frame, height=5, width=50)
        self.notes2_entry.insert("1.0", self.notes2.get())
        self.notes2_entry.grid(row=row, column=1, padx=10, pady=5, columnspan=2)
        self.notes2_entry.bind("<KeyRelease>", self.update_notes2)
        row += 1

        # File Paths Header
        file_paths_header = tk.Label(
            form_frame,
            text="File Paths",
            font=("Arial", 10, "bold"),
            bg="#7C889C",
            fg="white",
        )
        file_paths_header.grid(row=row, columnspan=2, pady=(20, 5), sticky="w")
        row += 1

        # Model Frame
        model_frame = tk.Frame(form_frame, bg="#7C889C")
        model_frame.grid(row=row, columnspan=2, pady=(10, 5))

        path_to_model_label = tk.Label(
            model_frame, text="Path to new model:", bg="#7C889C", fg="white"
        )
        path_to_model_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.model_entry = tk.Entry(
            model_frame, width=30, textvariable=self.default_model_path
        )
        self.model_entry.grid(row=0, column=1, padx=10, pady=5)
        browse_model_button = tk.Button(
            model_frame, text="Browse", command=self.browse_model
        )
        browse_model_button.grid(row=0, column=2, padx=5, pady=5)
        row += 1

        # Labels Frame
        labels_frame = tk.Frame(form_frame, bg="#7C889C")
        labels_frame.grid(row=row, columnspan=2, pady=(5, 10))

        path_to_label_file_label = tk.Label(
            labels_frame, text="Path to labels file:", bg="#7C889C", fg="white"
        )
        path_to_label_file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.labels_entry = tk.Entry(
            labels_frame, width=30, textvariable=self.default_labels_path
        )
        self.labels_entry.grid(row=0, column=1, padx=10, pady=5)
        browse_labels_button = tk.Button(
            labels_frame, text="Browse", command=self.browse_labels
        )
        browse_labels_button.grid(row=0, column=2, padx=5, pady=5)
        row += 1

        # Save Button
        save_button = tk.Button(
            self,
            text="Save",
            bg="#4CAF50",  # Green color for highlighting
            fg="white",
            font=("Arial", 12),
            command=self.save_constants,
            width=10,  # Adjust the width as needed
            height=2,  # Adjust the height as needed
            relief=tk.RAISED,  # Add a raised border
        )
        save_button.pack(pady=(10, 20))


if __name__ == "__main__":
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_close)  # Ensure clean exit
    app.mainloop()
