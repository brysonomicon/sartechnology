import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font as tkFont, ttk
from PIL import Image
from backend.led_controller import LEDController

from .shared_alert_controller import shared_alert
from .shared_confidence_controller import shared_confidence
from .settings1 import CustomSlider

# from backend.image_processor import ImageProcessor
from backend.sound_manager import SoundManager
from backend.image_saver import ImageSaver
from .shared_labels_controller import shared_labels
from .shared_segmentation_controller import shared_segmentation
import numpy as np
import datetime
import cv2
from jetson_wrapper.jetson_wrapper import cudaFromNumpy, cudaToNumpy


class MainFrame(tk.Frame):
    def __init__(self, parent, gps_manager, camera_feeds, color_scheme, **kwargs):
        super().__init__(parent, **kwargs)
        self.photo_2 = None
        self.confidence_slider = None
        self.category_dropdown = None
        self.confidence_controls_frame = None
        self.category_var = None
        self.color_scheme = color_scheme
        self.configure(bg="blue")
        self.parent = parent
        self.gps_manager = gps_manager
        self.camera_feeds = camera_feeds
        shared_confidence.register_observer(self.update_confidence)
        self.fullscreen_mode = None
        self.create_widgets()
        self.sound_manager = SoundManager()
        self.sound_manager.start()
        self.saver = ImageSaver({})
        self.saver.start()
        self.led_controller = LEDController()
        self.create_confidence_controls()
        shared_labels.add_observer(self.on_threshold_change)

        self.update_colors()

        self.parent.constants_manager.set_constant("camera_layout", "split")
        self.set_camera_layout("split")
        self.bind("<Configure>", self.on_resize)

    def create_confidence_controls(self):
        """Create the confidence slider with category dropdown"""
        # Determine theme colors
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        theme = self.color_scheme["colors"][mode]

        # Confidence controls frame
        self.confidence_controls_frame = tk.Frame(
            self.menu_options_frame,
            bg=theme["application/window_and_frame_color"],
            highlightbackground="black",
            highlightcolor="black",
            highlightthickness=2
        )
        self.confidence_controls_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Create a frame for the label and dropdown
        label_dropdown_frame = tk.Frame(
            self.confidence_controls_frame,
            bg=theme["application/window_and_frame_color"]
        )
        label_dropdown_frame.pack(side=tk.LEFT, padx=(10, 5))

        # Target label
        target_label = tk.Label(
            label_dropdown_frame,
            text="Target: ",
            bg=theme["application/window_and_frame_color"],
            fg="#D3D3D3",
            font=("Helvetica", 26)
        )
        target_label.pack(side=tk.LEFT)

        # Category dropdown
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            label_dropdown_frame,
            textvariable=self.category_var,
            state="readonly",
            font=("Helvetica", 30),
            width=15
        )

        # Get all available categories except BACKGROUND
        categories = [cat for cat in shared_labels.get_all_labels().keys() if cat != "BACKGROUND"]
        self.category_dropdown['values'] = categories
        if categories:
            self.category_var.set(categories[0])
            self.category_dropdown.current(0)
        self.category_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        self.category_dropdown.bind("<<ComboboxSelected>>", self.on_category_change)

        # Confidence slider
        self.confidence_slider = CustomSlider(
            self.confidence_controls_frame,
            id="confidence_slider",
            length=300,
            width=60,
            handle_size=30,
            bar_thickness=20,
            bg=theme["application/window_and_frame_color"],
            min_val=0,
            max_val=100,
            callback=self.on_confidence_change
        )

        # Set initial value and pack the slider
        selected_category = self.category_var.get()
        threshold = shared_labels.get_threshold(selected_category) * 100
        self.confidence_slider.set_value(threshold, update=False)
        self.confidence_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Optional: allow frame to expand with window
        self.confidence_controls_frame.grid_rowconfigure(1, weight=1)
        self.confidence_controls_frame.grid_columnconfigure(1, weight=1)

    def update_colors(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]

        self.configure(bg=color_scheme["application/window_and_frame_color"])
        self.menu_options_frame.configure(
            bg=color_scheme["application/window_and_frame_color"]
        )
        self.settings_button.configure(bg=color_scheme["selected_color"])
        self.confidence_slider_frame.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.confidence_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )
        self.confidence_slider.set_background_fill(
            color_scheme["slider_background_color"]
        )
        self.confidence_slider.set_bar_fill(color_scheme["slider_bar_fill"])
        self.confidence_slider.set_handle_fill(color_scheme["slider_knob_color"])
        self.confidence_slider.set_bar_outline(color_scheme["frame_outline_color"])

        self.gps_frame.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.confirm_quit_app_frame.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.confirm_quit_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )

        self.confirm_quit.configure(bg=color_scheme["selected_color"])
        self.dont_quit.configure(bg=color_scheme["apply_changes_background"])

    def update_confidence(self, value):
        # This method updates the slider's position and the label's text
        self.confidence_slider.set_value(value, update=False)  # Update the slider
        self.confidence_label.config(
            text=f"CONFIDENCE: {int(round(value))}%"
        )  # Update the label
        self.parent.ai.set_confidence(
            value / 100
        )  # Update the AI model's confidence threshold

    def on_slider_change(self, value):
        from shared_confidence_controller import shared_confidence

        shared_confidence.set_value(value)

    def create_widgets(self):
        # Camera frames
        self.camera_container = tk.Frame(self, bg="black")
        self.camera_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Bottom bar
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)  # Right sidebar


        self.create_cam_grid()

        self.update_camera = False

        custom_font = tkFont.Font(family="Helvetica", size=14, weight="bold")  # Increased font size

        # Menu options frame (below camera feeds)
        self.menu_options_frame = tk.Frame(self, bg="#7C889C", height=120)
        self.menu_options_frame.grid(row=1, column=0, columnspan=2, sticky="sew", padx=5, pady=5)
        self.menu_options_frame.grid_propagate(False)

        # Confidence slider frame
        self.confidence_slider_frame = tk.Frame(self.menu_options_frame, width=450, height=100,
                                                highlightbackground="black", highlightcolor="black",
                                                highlightthickness=2)
        self.confidence_slider_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.confidence_slider_frame.grid_propagate(False)

        self.confidence_label = tk.Label(
            self.confidence_slider_frame,
            text="CONFIDENCE: 50%",
            bg="#7C889C",
            fg="#D3D3D3",
            font=custom_font,
        )
        self.confidence_label.grid(row=0, column=0, sticky="nsw", pady=0)

        self.confidence_slider = CustomSlider(
            self.confidence_slider_frame,
            id="confidence_slider",
            length=200,
            width=60,
            handle_size=40,
            bar_thickness=40,
            bg="#7C889C",
            min_val=0,
            max_val=100,
            callback=self.update_confidence,
        )
        self.confidence_slider.grid(row=0, column=0, padx=(220,20), sticky="nse", pady=0)

        gps_font = tkFont.Font(family="Helvetica", size=22)

        # GPS frame
        self.gps_frame = tk.Frame(self.menu_options_frame, bg="#7C889C", width=600, height=100,
                                  highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.gps_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)
        self.gps_frame.grid_propagate(False)
        self.gps_coords_box = tk.Frame(self.gps_frame, bg="#7C889C")
        self.gps_coords_box.pack(fill="both", expand=True)
        self.gps_coords_title = tk.Label(self.gps_coords_box, text="LAT/LONG:", font=gps_font,
                                         fg="#D3D3D3", bg="#7C889C")
        self.gps_coords_value = tk.Label(self.gps_coords_box, text="49.000000, -123.000000", font=gps_font,
                                         fg="#24D215", bg="#7C889C")
        self.gps_coords_title.pack(side=tk.LEFT)
        self.gps_coords_value.pack(side=tk.LEFT, padx=(0, 10))
        self.gps_coords_box.grid_rowconfigure(0, weight=1)
        self.gps_coords_box.grid_columnconfigure(0, weight=1)
        self.gps_coords_title.pack(side=tk.LEFT, padx=(20, 5), pady=10)
        self.gps_coords_value.pack(side=tk.LEFT, pady=10)

        # self.gps_coords_box.place(relx=0.5, rely=0.5, anchor="center")

        # Back button (initially hidden)
        self.back_btn = tk.Button(
            self, text="← Back", font=("Arial", 14),
            command=self.exit_fullscreen,
            bg="gray", fg="white", bd=0)
        self.back_btn.place(relx=0.95, rely=0.05, anchor="ne")

        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        colors = self.color_scheme["colors"][mode]

        self.back_btn = tk.Button(
            self, text="← Back", font=("Arial", 14),
            command=self.exit_fullscreen,
            bg=colors["fullscreen_button_bg"],
            fg=colors["fullscreen_button_fg"],
            bd=0, relief="flat")

        # Right sidebar for GPS info + Exit
        self.grid_columnconfigure(2, weight=0)
        self.right_sidebar_frame = tk.Frame(self, bg="#7C889C", width=100)
        self.right_sidebar_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(5, 5), pady=5)



        # ---- Setup Section Above GPS Data ----

        # mute stuff
        self.mute_alerts_frame = tk.Frame(
            self.right_sidebar_frame,
            width=200,
            height=120,
            highlightbackground="black",
            highlightcolor="black",
            highlightthickness=2,
            bg="#7C889C"
        )
        self.mute_alerts_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.mute_alerts_frame.pack_propagate(False)

        mute_label = tk.Label(
            self.mute_alerts_frame,
            text="Mute Alerts",
            font=("Helvetica", 18, "bold"),
            bg="#7C889C",
            fg="#D3D3D3"
        )
        mute_label.pack(pady=(10, 5))

        self.mute_var = tk.BooleanVar(value=False)
        self.mute_checkbox = tk.Checkbutton(
            self.mute_alerts_frame,
            variable=self.mute_var,
            bg="#7C889C",
            activebackground="#7C889C",
            selectcolor="#7C889C",
            fg="#24D215",
            font=("Helvetica", 22, "bold"),
            indicatoron=True,
            onvalue=True,
            offvalue=False
        )
        self.mute_checkbox.pack(pady=(0, 5))

        # SETUP label
        setup_label = tk.Label(
            self.right_sidebar_frame,
            text="SETUP",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg=self.right_sidebar_frame["bg"]
        )
        setup_label.pack(pady=(15, 5))

        # CAMERA button
        self.settings_button = tk.Button(
            self.right_sidebar_frame,
            bg="#24D215",
            fg="white",
            text="CAMERA",
            font=("Helvetica", 18, "bold"),
            width=16,
            height=1,
            command=self.on_settings_click,
            relief="raised",
            bd=3
        )
        self.settings_button.pack(fill="x", padx=10, pady=(0, 5))

        # DETECTION button
        self.settings2_button = tk.Button(
            self.right_sidebar_frame,
            bg="#24D215",
            fg="white",
            text="DETECTION",
            font=("Helvetica", 18, "bold"),
            width=16,
            height=1,
            command=self.on_settings2_click,
            relief="raised",
            bd=3
        )
        self.settings2_button.pack(fill="x", padx=10, pady=(0, 15))

        # GPS Time Label
        self.gps_time_box = tk.Frame(self.right_sidebar_frame, bg=colors["application/window_and_frame_color"],
                                     highlightbackground="black", highlightthickness=3)
        self.gps_time_title = tk.Label(self.gps_time_box, text="DATE/TIME", font=("Helvetica", 18, "bold"),
                                       bg=colors["application/window_and_frame_color"], fg="#D3D3D3")
        self.gps_time_value = tk.Label(self.gps_time_box, text="16 MAY\n2024 PST\n18:59:49",
                                       font=("Helvetica", 18, "bold"), bg=colors["application/window_and_frame_color"],
                                       fg="#24D215", justify="center")
        self.gps_time_title.pack()
        self.gps_time_value.pack()
        self.gps_time_box.pack(fill="x", padx=5, pady=(10, 5))

        # Altitude Box
        self.altitude_box = tk.Frame(self.right_sidebar_frame, bg=colors["application/window_and_frame_color"],
                                     highlightbackground="black", highlightthickness=3)
        self.altitude_title = tk.Label(self.altitude_box, text="ALT", font=("Helvetica", 18, "bold"),
                                       bg=colors["application/window_and_frame_color"], fg="#D3D3D3")
        self.altitude_value = tk.Label(self.altitude_box, text="188.7 ft", font=("Helvetica", 18, "bold"),
                                       bg=colors["application/window_and_frame_color"], fg="#24D215")
        self.altitude_title.pack()
        self.altitude_value.pack()
        self.altitude_box.pack(fill="x", padx=5, pady=5)

        # Bearing Box (COG)
        self.bearing_box = tk.Frame(self.right_sidebar_frame, bg=colors["application/window_and_frame_color"],
                                    highlightbackground="black", highlightthickness=3)
        self.bearing_title = tk.Label(self.bearing_box, text="COG", font=("Helvetica", 18, "bold"),
                                      bg=colors["application/window_and_frame_color"], fg="#D3D3D3")
        self.bearing_value = tk.Label(self.bearing_box, text="--- Deg T", font=("Helvetica", 18, "bold"),
                                      bg=colors["application/window_and_frame_color"], fg="#24D215")
        self.bearing_title.pack()
        self.bearing_value.pack()
        self.bearing_box.pack(fill="x", padx=5, pady=5)

        # Speed Box
        self.speed_box = tk.Frame(self.right_sidebar_frame, bg=colors["application/window_and_frame_color"],
                                  highlightbackground="black", highlightthickness=3)
        self.speed_title = tk.Label(self.speed_box, text="GND SPD", font=("Helvetica", 18, "bold"),
                                    bg=colors["application/window_and_frame_color"], fg="#D3D3D3")
        self.speed_value = tk.Label(self.speed_box, text="42.3 Km/Hr", font=("Helvetica", 18, "bold"),
                                    bg=colors["application/window_and_frame_color"], fg="#24D215")
        self.speed_title.pack()
        self.speed_value.pack()
        self.speed_box.pack(fill="x", padx=5, pady=5)



        # Exit Button (styled to fit)
        self.exit_btn = tk.Button(
            self.right_sidebar_frame, text="EXIT", bg="red", fg="white",
            font=("Helvetica", 18, "bold"), command=self.show_confirm_quit_app_frame,
            relief="raised", bd=3, height=2
        )
        tk.Label(self.right_sidebar_frame, bg=colors["application/window_and_frame_color"]).pack(expand=True)
        self.exit_btn.pack(side="bottom", fill="x", padx=5, pady=10)


        # Confirm quit frame
        self.confirm_quit_app_frame = tk.Frame(
            self, bg="#7C889C", width=350, height=120,
            highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.confirm_quit_label = tk.Label(
            self.confirm_quit_app_frame, text="ARE YOU SURE YOU WANT TO QUIT\nTHE APPLICATION?",
            bg="#7C889C", fg="#D3D3D3", font=custom_font)
        self.confirm_quit_label.place(x=10, y=15)
        self.confirm_quit = tk.Button(
            self.confirm_quit_app_frame, bg="#24D215", fg="white", font=custom_font,
            text="YES", command=self.parent.quit_application, width=12, height=1)
        self.confirm_quit.place(x=40, y=70)
        self.dont_quit = tk.Button(
            self.confirm_quit_app_frame, bg="red", fg="white", font=custom_font,
            text="NO", command=self.dont_quit_app, width=12, height=1)
        self.dont_quit.place(x=180, y=70)

        tk.Label(self.right_sidebar_frame, bg=colors["application/window_and_frame_color"]).pack(expand=True)

        self.start_gps_thread()
        self.update_time()

        #############################################################################################################

    def show_confirm_quit_app_frame(self):
        self.confirm_quit_app_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.confirm_quit_app_frame.lift()
        self.confirm_quit_app_frame.focus_set()

    def dont_quit_app(self):
        self.confirm_quit_app_frame.place_forget()

    # Camera methods
    def start_camera_feed(self):
        self.update_camera = True
        self.update_frame()

    def stop_camera_feed(self):
        self.update_camera = False

    def on_settings2_click(self):
        self.parent.switch_settings2()

    def update_frame(self):
        if self.update_camera:
            try:
                detections = []
                img_np = None

                # Get current layout mode
                layout_mode = self.parent.constants_manager.get_constant("camera_layout", "split")

                for inx, camera in enumerate(self.camera_feeds):
                    if not camera.is_connected():
                        self.camera_labels[inx].config(image="", text='Not Connected')
                        continue

                    ret, frame = camera.read()

                    if not ret or frame is None or frame.shape[0] < 100:
                        self.camera_labels[inx].config(
                            image="",
                            text="No Feed\n(Connected, but no signal)",
                            fg="red",
                            font=("Helvetica", 16, "bold")
                        )
                        continue

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Determine target size
                    layout_mode = self.parent.constants_manager.get_constant("camera_layout", "split")
                    if layout_mode == f"camera{inx + 1}" or self.fullscreen_mode == f"camera{inx + 1}":
                        target_width = self.winfo_width()
                        target_height = self.winfo_height()
                    else:
                        num_cams = len(self.camera_feeds)
                        cols = 1 if num_cams == 1 else 2 if num_cams <= 4 else 3
                        rows = (num_cams + cols - 1) // cols
                        target_width = self.winfo_width() // cols
                        target_height = (self.winfo_height() - self.menu_options_frame.winfo_height()) // rows

                    frame = cv2.resize(frame, (target_width, target_height))
                    cuda_frame = cudaFromNumpy(frame)

                    cam_detections = self.parent.ai.detect(cuda_frame)
                    img_np = cudaToNumpy(cuda_frame)

                    img_pil = Image.fromarray(img_np)
                    photo = ImageTk.PhotoImage(image=img_pil)
                    self.camera_labels[inx].config(image=photo)
                    self.camera_labels[inx].image = photo  # prevent GC
                    self.camera_labels[inx].update_idletasks()

                    if cam_detections:
                        if cam_detections:
                            print(f"Detections from camera {inx + 1}: {len(cam_detections)}")
                            self.handle_detections(cam_detections, img_np, camera_id=inx)

            except Exception as e:
                print(f"Camera processing error: {str(e)}")

            self.after(30, self.update_frame)  # ~30 FPS

    def handle_detections(self, detections, img, camera_id=None):
        self.led_controller.flash_led()
        self.sound_manager.play_sound(detections)
        try:
            lat, lon = self.gps_manager.get_coords()
            altitude = self.gps_manager.get_latest_altitude()
            speed = self.gps_manager.get_latest_speed()
            bearing = self.gps_manager.get_latest_bearing()

            gps_coords = {
                "latitude": lat,
                "longitude": lon,
                "altitude": altitude,
                "speed_kmh": speed,
                "course_deg": bearing,
                "camera_id": camera_id,
            }

        except ValueError:
            gps_coords = None

        self.saver.add_image(img, detections, gps_coords)

    def start_gps_thread(self):
        self.gps_manager.start()
        self.update_gps_data()

    def update_gps_data(self):
        # Update GPS coordinates
        try:
            coords = self.gps_manager.get_coords()
            if coords is not None:
                lat, lon = coords
                self.gps_coords_title.config(text="LAT/LONG: ")
                self.gps_coords_value.config(text=f"{lat:.6f}, {lon:.6f}")
            else:
                self.gps_coords_title.config(text="LAT/LONG: ")
                self.gps_coords_value.config(text="Not Connected")
        except ValueError:
            self.gps_coords_title.config(text="LAT/LONG: ")
            self.gps_coords_value.config(text="Not Connected")

        # Update Altitude
        try:
            altitude = self.gps_manager.get_latest_altitude()
            if altitude is not None:
                self.altitude_title.config(text="ALT")
                self.altitude_value.config(text=f"{altitude} FT")
            else:
                self.altitude_title.config(text="ALT")
                self.altitude_value.config(text="Not Connected")
        except ValueError:
            self.altitude_title.config(text="ALT")
            self.altitude_value.config(text="Not Connected")

        # Speed
        try:
            speed = self.gps_manager.get_latest_speed()
            if speed is not None:
                speed_kmh = round(speed * 3.6, 1)
                self.speed_title.config(text="GND SPD")
                self.speed_value.config(text=f"{speed_kmh} Km/Hr")
            else:
                self.speed_title.config(text="GND SPD")
                self.speed_value.config(text="Not Connected")
        except ValueError:
            self.speed_title.config(text="GND SPD")
            self.speed_value.config(text="Not Connected")

        # Bearing
        try:
            bearing = self.gps_manager.get_latest_bearing()
            if bearing is not None:
                self.bearing_title.config(text="COG")
                self.bearing_value.config(text=f"{bearing} Deg T")
            else:
                self.bearing_title.config(text="COG")
                self.bearing_value.config(text="Not Connected")
        except ValueError:
            self.bearing_title.config(text="COG")
            self.bearing_value.config(text="Not Connected")

        # Retry in 1 second
        self.after(1000, self.update_gps_data)

    def on_settings_click(self):
        self.parent.switch_settings1()

    def toggle_fullscreen(self, camera):
        """Toggle fullscreen mode for specified camera"""
        if self.fullscreen_mode == camera:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen(camera)

    def enter_fullscreen(self, camera):
        """Enter fullscreen mode for specified camera"""
        self.fullscreen_mode = camera

        for frame in self.camera_frames:
            frame.grid_remove()

        try:
            inx = int(camera.replace("camera", "")) - 1  # zero-based index
            self.camera_frames[inx].grid(row=0, column=0, sticky="nsew")
            self.camera_container.grid_rowconfigure(0, weight=1)
            self.camera_container.grid_columnconfigure(0, weight=1)
            # self.fullscreen_btns[inx].place_forget()
        except (ValueError, IndexError):
            print(f"[FullScreen Error] Invalid camera index: {camera}")

        self.back_btn.place(relx=0.95, rely=0.05, anchor="ne")

    def exit_fullscreen(self):
        self.fullscreen_mode = None
        self.back_btn.place_forget()
        self.menu_options_frame.grid()
        self.parent.constants_manager.set_constant("camera_layout", "split")
        self.set_camera_layout("split")

    def set_camera_layout(self, layout):
        self.fullscreen_mode = layout

        # Clear all camera_container rows and columns
        for i in range(6):
            self.camera_container.grid_rowconfigure(i, weight=0)
            self.camera_container.grid_columnconfigure(i, weight=0)

        # Remove all existing camera frames from camera_container
        for frame in self.camera_frames:
            frame.grid_remove()

        if layout == "split":
            num_cams = len(self.camera_frames)
            if num_cams <= 1:
                cols = 1
            elif num_cams == 2:
                cols = 2
            elif num_cams <= 4:
                cols = 2
            else:
                cols = 3

            for inx, frame in enumerate(self.camera_frames):
                row = inx // cols
                col = inx % cols
                frame.grid(in_=self.camera_container, row=row, column=col, sticky="nsew")
                self.camera_container.grid_rowconfigure(row, weight=1)
                self.camera_container.grid_columnconfigure(col, weight=1)

        elif layout.startswith("camera"):
            try:
                cam_inx = int(layout.replace("camera", "")) - 1
                if 0 <= cam_inx < len(self.camera_frames):
                    self.camera_frames[cam_inx].grid(in_=self.camera_container, row=0, column=0, sticky="nsew")
                    self.camera_container.grid_rowconfigure(0, weight=1)
                    self.camera_container.grid_columnconfigure(0, weight=1)
            except ValueError:
                print(f"Invalid layout mode: {layout}")

    def on_category_change(self, event):
        """Update slider when category changes"""
        selected_category = self.category_var.get()
        threshold = shared_labels.get_threshold(selected_category) * 100
        self.confidence_slider.set_value(threshold, update=False)
        self.confidence_label.config(text=f"CONFIDENCE: {int(threshold)}%")

    def on_confidence_change(self, value):
        """Update threshold when slider changes"""
        selected_category = self.category_var.get()
        clamped_value = max(2, value)
        threshold = clamped_value / 100  # Convert from percentage to decimal
        shared_labels.set_threshold(selected_category, threshold)
        self.confidence_label.config(text=f"CONFIDENCE: {int(value)}%")
        self.confidence_slider.set_value(clamped_value, update=False)

    def on_threshold_change(self, label, threshold):
        """
        Update the slider when the threshold is changed in the settings.
        :param label: The label whose threshold has changed.
        :param threshold: The new threshold value.
        :return: None
        """
        if self.category_var and self.category_var.get() == label:
            self.confidence_slider.set_value(threshold * 100, update=False)
            self.confidence_label.config(text=f"CONFIDENCE: {int(threshold * 100)}%")

    def on_resize(self, event):
        self.update_camera_sizes()

    def update_camera_sizes(self):
        self.update_idletasks()
        total_width = self.winfo_width()
        total_height = self.winfo_height() - self.menu_options_frame.winfo_height()

        for frame in self.camera_frames:
            frame.config(width=0, height=0)

        # if done via the fs button (temporaru)
        if self.fullscreen_mode and self.fullscreen_mode.startswith("camera"):
            try:
                cam_inx = int(self.fullscreen_mode.replace("camera", "")) - 1
                if 0 <= cam_inx < len(self.camera_frames):
                    self.camera_frames[cam_inx].config(width=total_width, height=total_height)
            except ValueError:
                print(f"Invalid camera index: {self.fullscreen_mode}")
                pass
            return  # early exit so it doesnt apply the layour

        layout = self.parent.constants_manager.get_constant("camera_layout", "split")

        # if done in the settings (non temporary)
        if layout.startswith("camera"):
            try:
                cam_inx = int(layout.replace("camera", "")) - 1
                if 0 <= cam_inx < len(self.camera_frames):
                    self.camera_frames[cam_inx].config(width=total_width, height=total_height)
                    return
            except ValueError:
                pass

        num_cams = len(self.camera_frames)
        if num_cams <= 1:
            cols = 1
        elif num_cams == 2:
            cols = 2
        elif num_cams <= 4:
            cols = 2
        else:
            cols = 3

        rows = (num_cams + cols - 1) // cols

        for inx, frame in enumerate(self.camera_frames):
            frame.config(
                width=total_width // cols,
                height=total_height // rows
            )

    def update_time(self):
        """Update the GPS time label every second."""
        now = datetime.datetime.now()
        formatted = now.strftime("%d %b\n%Y PST\n%H:%M:%S").upper()
        self.gps_time_value.config(text=formatted)
        self.after(1000, self.update_time)  # call again after 1 second

    def create_cam_grid(self):
        """
        Create a grid of camera frames based on the number of camera feeds.
        To support 6 cameras, the layout will be based on the number of cameras
        and will be arranged in a grid format.
        """
        self.camera_frames = []  # List to hold camera frames
        self.camera_labels = []  # List to hold camera labels
        self.fullscreen_btns = []  # List to hold fullscreen buttons

        num_cams = len(self.camera_feeds)
        if num_cams <= 1:
            rows, cols = 1, 1
        elif num_cams == 2:
            rows, cols = 1, 2
        elif num_cams <= 4:
            rows, cols = 2, 2
        else:
            rows, cols = 2, 3

        inx = 0
        for row in range(rows):
            for col in range(cols):
                if inx >= num_cams:
                    break

                cam_frame = tk.Frame(self.camera_container, bg="black", borderwidth=1, relief="solid")
                cam_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                cam_frame.grid_propagate(False)

                cam_label = tk.Label(cam_frame, bg="black")
                cam_label.pack(expand=True, fill="both")

                fs_btn = tk.Button(cam_frame, text="⛶", font=("Arial", 14),
                                   command=lambda i=inx: self.toggle_fullscreen(f"camera{i + 1}"),
                                   bg="gray", fg="white", bd=0)

                fs_btn.place(relx=0.95, rely=0.05, anchor="ne")

                self.camera_frames.append(cam_frame)
                self.camera_labels.append(cam_label)
                self.fullscreen_btns.append(fs_btn)
                inx += 1

        for row in range(rows):
            self.camera_container.grid_rowconfigure(row, weight=1)
        for col in range(cols):
            self.camera_container.grid_columnconfigure(col, weight=1)