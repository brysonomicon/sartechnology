import tkinter as tk
from tkinter import font as tkFont
from tkinter import ttk

from .shared_confidence_controller import shared_confidence
from .application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager

class SettingsFrame1(tk.Frame):
    def __init__(self, parent, camera_feeds, application, color_scheme, **kwargs):
        super().__init__(parent, **kwargs)
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.application = application
        self.color_scheme = color_scheme
        self.focus_mode = tk.StringVar(value="Automatic")
        self.camera_feeds = camera_feeds
        self.current_cam = tk.IntVar(value=0)
        self.style = ttk.Style()
        self.default_settings_pushed = True
        self.create_widgets()
        self.update_colors()

    def create_widgets(self):
        font_used = tkFont.Font(family="Helvetica", size=18, weight="bold")  # Scaled-up font
        section_padx = 30
        section_pady = 20

        self.sliders_frame = tk.Frame(self)
        self.sliders_frame.grid(row=0, column=0, padx=section_padx, pady=section_pady, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.sliders_frame.grid_columnconfigure(0, weight=1)
        self.sliders_frame.grid_columnconfigure(1, weight=1)

        # Section 1: Camera Selection
        self.camera_section = tk.LabelFrame(self.sliders_frame, text="Camera Settings", font=font_used, padx=20, pady=20)
        self.camera_section.grid(row=0, column=0, columnspan=2, sticky="ew", pady=section_pady)

        self.cam_btns = []
        self.cam_status_labels = []

        self.cam_select_label = tk.Label(self.camera_section, text="Select Camera Input", font=font_used)
        self.cam_select_label.grid(row=0, column=0, columnspan=6, pady=(0, 5))

        self.cam_hint_label = tk.Label(
            self.camera_section,
            text=(
                "If no camera feed is detected,\n"
                "Check Lens Cap, Brightness, and Focus.\n"
                "Only two plugged-in cameras can be displayed at the same time.\n"
                "Close and re-open the scanner to activate both plugged-in cameras."
            ),
            font=("Helvetica", 13, "italic"),
            fg="#D3D3D3",
            bg=self.color_scheme["colors"]["dark" if self.color_scheme["dark_mode"] else "light"][
                "application/window_and_frame_color"
            ],
            wraplength=700,
            justify="center"
        )
        self.cam_hint_label.grid(row=1, column=0, columnspan=7, pady=(0, 10))

        # Update the button and status label loop to use row=2 and row=3:
        for i, feed in enumerate(self.camera_feeds):
            btn = tk.Button(self.camera_section, text=f"CAMERA {i + 1}", font=font_used, width=22, height=2,
                            command=lambda idx=i: self.set_camera_mode(f"camera{idx + 1}"))
            btn.grid(row=2, column=i, padx=10, pady=10)
            self.cam_btns.append(btn)

            lbl = tk.Label(self.camera_section, text="(Unknown)", font=("Helvetica", 12, "italic"))
            lbl.grid(row=3, column=i, pady=(0, 10))
            self.cam_status_labels.append(lbl)

        self.split_view_button = tk.Button(self.camera_section, text="ALL CAMERAS", font=font_used, width=22, height=2,
                                           command=lambda: self.set_camera_mode("split"))
        self.split_view_button.grid(row=2, column=len(self.camera_feeds), padx=10, pady=10)

        # Section 2: Resolution
        self.resolution_section = tk.LabelFrame(self.sliders_frame, text="Resolution Settings", font=font_used, padx=20,
                                                pady=20)
        self.resolution_section.grid(row=1, column=0, sticky="ew", pady=section_pady)

        self.resolution_label = tk.Label(self.resolution_section, text="Select Resolution", font=font_used)
        self.resolution_label.pack(anchor="w", pady=10)

        selected_option = tk.StringVar(value="1920x1080 pixels")
        options = ["1280x720 pixels", "1920x1080 pixels", "2560x1440 pixels", "3840x2160 pixels"]
        self.option_menu = ttk.OptionMenu(self.resolution_section, selected_option, selected_option.get(), *options,
                                          command=self.selection_changed)
        self.option_menu.pack(fill="x", pady=10)

        # Section 3: Operator Notes + Comments
        self.notes_section = tk.LabelFrame(self.sliders_frame, text="Operator Notes & Comments", font=font_used,
                                           padx=20, pady=20)
        self.notes_section.grid(row=2, column=0, sticky="ew", pady=section_pady)

        self.open_notes_button = tk.Button(self.notes_section, text="Open Operator Notes", font=font_used,
                                           command=self.show_operator_notes, width=40, height=2)
        self.open_notes_button.pack(pady=10)

        self.open_comments_button = tk.Button(self.notes_section, text="Open Operator Comments", font=font_used,
                                              command=self.show_operator_comments, width=40, height=2)
        self.open_comments_button.pack(pady=10)

        # Section 4: Misc Settings
        self.misc_section = tk.LabelFrame(self.sliders_frame, text="Other Settings", font=font_used, padx=20, pady=20)
        self.misc_section.grid(row=1, column=1, sticky="ew", pady=section_pady)

        self.default_settings_button = tk.Button(self.misc_section, text="DEFAULT SETTINGS", font=font_used,
                                                 width=30, height=3, command=self.default_setings_selection)
        self.default_settings_button.grid(row=0, column=0, padx=15, pady=10)

        self.custom_settings_button = tk.Button(self.misc_section, text="CUSTOM SETTINGS", font=font_used,
                                                width=30, height=3, command=self.custom_settings_selection)
        self.custom_settings_button.grid(row=0, column=1, padx=(15, 40), pady=10)


        # Section 5: Exit Button
        self.close_menu_button_frame = tk.Frame(self, width=80, height=80)
        self.close_menu_button_frame.grid(row=0, column=1, padx=20, pady=20, sticky="ne")
        self.close_menu_button_frame.grid_propagate(False)

        x_button_font = tkFont.Font(family="Helvetica", size=26, weight="bold")
        self.close_menu_button = tk.Button(self.close_menu_button_frame, text="X", bg="red", fg="white",
                                           font=x_button_font, command=self.master.switch_main_frame)
        self.close_menu_button.pack(ipadx=10, ipady=10, expand=True)

        # Operator Text Fields
        self.text_field_frame = tk.Frame(self, bg="black", height=600, width=1900,
                                         highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.text_field = tk.Text(self.text_field_frame, bg="white", font=("Helvetica", 16), fg="black", height=30,
                                  width=150)
        self.text_field.place(x=0, y=0)
        self.text_field.insert("1.0", self.constants_manager.get_constant("operator_notes"))

        self.save_button = tk.Button(self.text_field_frame, text="SAVE", bg="#24D215", fg="white", font=font_used,
                                     height=2, width=30, command=self.save_notes_input)
        self.save_button.place(relx=0.85, rely=0.9, anchor="se")

        self.comments_text_field_frame = tk.Frame(self, bg="black", height=600, width=1900,
                                                  highlightbackground="black", highlightcolor="black",
                                                  highlightthickness=2)
        self.comments_text_field = tk.Text(self.comments_text_field_frame, bg="white", font=("Helvetica", 16),
                                           fg="black",
                                           height=30, width=150)
        self.comments_text_field.place(x=0, y=0)
        self.comments_text_field.insert("1.0", self.constants_manager.get_constant("operator_comments"))

        self.save_comments_button = tk.Button(self.comments_text_field_frame, text="SAVE COMMENTS", bg="#24D215",
                                              fg="white",
                                              font=font_used, height=2, width=30, command=self.save_comments_input)
        self.save_comments_button.place(relx=0.85, rely=0.9, anchor="se")

        # Dark Mode Toggle
        self.darkmode_toggle_frame = tk.Frame(self.sliders_frame, bg="#7C889C", highlightbackground="black",
                                              highlightcolor="black", highlightthickness=2, width=500, height=180)
        self.darkmode_toggle_frame.grid(row=2, column=1, sticky="ew", pady=section_pady)

        self.darkmode_label = tk.Label(self.darkmode_toggle_frame, text="Dark Mode", font=font_used,
                                        bg="#7C889C", fg="black")

        self.darkmode_label.place(x=40, y=70)
        darkmode_switch_state = {"is_on": self.color_scheme["dark_mode"]}
        self.darkmode_toggle_canvas = tk.Canvas(
            self.darkmode_toggle_frame, width=160, height=80, bg="#7C889C",
            highlightthickness=0
        )
        self.darkmode_toggle_canvas.place(x=300, y=60)
        self.darkmode_switch_background = self.darkmode_toggle_canvas.create_rectangle(
            5, 10, 155, 70,
            fill="#006400" if darkmode_switch_state["is_on"] else "#697283"
        )
        switch_coords = (100, 10, 140, 50) if darkmode_switch_state["is_on"] else (10, 10, 50, 50)
        self.darkmode_switch = self.darkmode_toggle_canvas.create_oval(*switch_coords, fill="white", outline="white")

        self.darkmode_toggle_canvas.tag_bind(
            self.darkmode_switch, "<Button-1>",
            lambda event: self.toggle_darkmode_switch(
                self.darkmode_toggle_canvas, self.darkmode_switch_background,
                self.darkmode_switch, darkmode_switch_state
            )
        )

        self.update_camera_selection()

        #############################################################################################################

    def update_colors(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]

        self.configure(bg=color_scheme["application/window_and_frame_color"])
        self.sliders_frame.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.camera_section.configure(bg=color_scheme["application/window_and_frame_color"])
        self.cam_select_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )

        for i, button in enumerate(self.cam_btns):
            is_active = self.current_cam.get() == i
            button.configure(
                bg=(
                    color_scheme["focus_button_bg_dark_active"]
                    if mode == "dark" and is_active
                    else color_scheme["focus_button_bg_dark_inactive"]
                    if mode == "dark"
                    else color_scheme["focus_button_bg_light_active"]
                    if is_active
                    else color_scheme["focus_button_bg_light_inactive"]
                )
            )

        is_split = self.current_cam.get() == -1
        self.split_view_button.configure(
            bg=(
                color_scheme["focus_button_bg_dark_active"]
                if mode == "dark" and is_split
                else color_scheme["focus_button_bg_dark_inactive"]
                if mode == "dark"
                else color_scheme["focus_button_bg_light_active"]
                if is_split
                else color_scheme["focus_button_bg_light_inactive"]
            )
        )

        self.resolution_section.configure(bg=color_scheme["application/window_and_frame_color"])
        self.resolution_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )

        self.notes_section.configure(bg=color_scheme["application/window_and_frame_color"])
        self.open_notes_button.configure(bg=color_scheme["settings_select_buttons_inactive"])
        self.open_comments_button.configure(bg=color_scheme["settings_select_buttons_inactive"])

        self.misc_section.configure(bg=color_scheme["application/window_and_frame_color"])
        self.default_settings_button.configure(
            bg=color_scheme["selected_color"] if self.default_settings_pushed else color_scheme[
                "settings_select_buttons_inactive"]
        )
        self.custom_settings_button.configure(
            bg=color_scheme["settings_select_buttons_inactive"] if self.default_settings_pushed else color_scheme[
                "selected_color"]
        )

        self.close_menu_button.configure(bg=color_scheme["apply_changes_background"])

        self.style.map(
            "TMenubutton",
            background=[("active", color_scheme["selected_color"]), ("!active", color_scheme["button_bg"])],
            foreground=[("active", color_scheme["button_font_color/fg"]),
                        ("!active", color_scheme["button_font_color/fg"])],
        )
        self.style.configure(
            "TMenubutton",
            background=color_scheme["button_bg"],
            foreground=color_scheme["button_font_color/fg"],
        )
        self.style.configure(
            "TMenu",
            background=color_scheme["button_bg"],
            foreground=color_scheme["button_font_color/fg"],
            borderwidth=0,
        )
        self.style.map("TMenu", background=[("active", color_scheme["selected_color"])])

    def toggle_darkmode_switch(
            self, switch_canvas, switch_background, switch_indicator, switch_state
    ):
        switch_state["is_on"] = not switch_state["is_on"]

        if switch_state["is_on"]:
            switch_canvas.itemconfig(switch_background, fill="#006400")
            switch_canvas.coords(switch_indicator, 100, 10, 140, 50)
        else:
            switch_canvas.itemconfig(switch_background, fill="#697283")
            switch_canvas.coords(switch_indicator, 10, 10, 50, 50)

        # Call the method on the Application class to update all frames
        self.update_colors()
        self.application.toggle_dark_mode()

    def update_camera_selection(self):
        feeds = self.camera_feeds

        for i, status_label in enumerate(self.cam_status_labels):
            feed = feeds[i] if i < len(feeds) else None
            if feed is not None and feed.is_connected():
                status_label.config(text="(Connected)")
            else:
                status_label.config(text="(Not Connected)")

        self.update_camera_buttons()

    def selection_changed(self, value):
        print(f"I DO NOTHING FOR NOW {value}")

    def save_notes_input(self):
        input_value = self.text_field.get(
            "1.0", tk.END
        )  # Retrieves the text from the Text widget
        print(input_value)
        self.text_field_frame.place_forget()
        self.constants_manager.set_constant("operator_notes", input_value)
        # This function should be responsible for saving what's written in the notes section

    def save_comments_input(self):
        input_value = self.comments_text_field.get("1.0", tk.END)
        print(input_value)
        self.constants_manager.set_constant("operator_comments", input_value)
        self.comments_text_field_frame.place_forget()

    def default_setings_selection(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]
        self.default_settings_button.configure(bg=color_scheme["selected_color"])
        self.custom_settings_button.configure(
            bg=color_scheme["settings_select_buttons_inactive"]
        )
        self.default_settings_pushed = True

    def custom_settings_selection(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]
        self.default_settings_button.configure(
            bg=color_scheme["settings_select_buttons_inactive"]
        )
        self.custom_settings_button.configure(bg=color_scheme["selected_color"])
        self.default_settings_pushed = False

    def show_operator_notes(self):
        self.text_field_frame.place(x=20, y=18)

    def show_operator_comments(self):
        self.comments_text_field_frame.place(x=20, y=18)

    def set_camera_mode(self, mode):
        self.constants_manager.set_constant("camera_layout", mode)
        self.application.main_frame.set_camera_layout(mode)

        if mode.startswith("camera"):
            try:
                index = int(mode.replace("camera", "")) - 1
                self.current_cam.set(index)
            except ValueError:
                self.current_cam.set(-1)
        else:
            self.current_cam.set(-1)

        self.update_camera_buttons()

    def update_camera_buttons(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]
        cam_mode = self.constants_manager.get_constant("camera_layout", "split")

        active = (
            color_scheme["focus_button_bg_dark_active"]
            if mode == "dark"
            else color_scheme["focus_button_bg_light_active"]
        )
        inactive = (
            color_scheme["focus_button_bg_dark_inactive"]
            if mode == "dark"
            else color_scheme["focus_button_bg_light_inactive"]
        )

        for i, button in enumerate(self.cam_btns):
            button.configure(
                bg=active if cam_mode == f"camera{i + 1}" else inactive
            )

        self.split_view_button.configure(
            bg=active if cam_mode == "split" else inactive
        )


class CustomSlider(tk.Canvas):
    def __init__(self, parent, id, length=300, width=80, handle_size=30, bar_thickness=20,
                 min_val=0, max_val=100, bg="black", callback=None, bar_fill="#697283",
                 bar_outline="black", handle_fill="#24D215", **kwargs):
        kwargs.pop("command", None)
        super().__init__(parent, height=width, width=length, bg=bg, highlightthickness=0, **kwargs)
        self.callback = callback
        self.length = length
        self.width = width
        self.handle_size = handle_size
        self.bar_thickness = bar_thickness
        self.min_val = min_val
        self.max_val = max_val
        self.id = id
        self.value = 50  # Default starting value
        self.bg = bg
        self.bar_fill = bar_fill
        self.bar_outline = bar_outline
        self.handle_fill = handle_fill

        self.percentage_label = tk.Label(self, text="50%", bg=bg, fg="white",
                                         font=("Helvetica", 12, "bold"))
        self.percentage_label.place(x=length // 2 - 15, y=width - 20)

        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.draw_slider()

    def draw_slider(self):
        self.delete("all")
        padding = self.handle_size // 2

        # Draw the slider bar
        self.create_rectangle(
            padding,
            self.width // 2 - self.bar_thickness // 2 - 10,  # Position higher
            self.length - padding,
            self.width // 2 + self.bar_thickness // 2 - 10,  # Position higher
            fill=self.bar_fill,
            outline=self.bar_outline,
            width=2,
        )

        # Calculate the handle position based on the current value
        handle_position = self.value_to_position(self.value)

        # Draw the handle with a custom fill color
        self.create_oval(
            handle_position - self.handle_size // 2,
            self.width // 2 - self.handle_size // 2 - 10,  # Position higher
            handle_position + self.handle_size // 2,
            self.width // 2 + self.handle_size // 2 - 10,  # Position higher
            fill=self.handle_fill,
            outline="white",
            width=2
        )

        self.percentage_label.config(text=f"{int(self.value)}%")
        self.percentage_label.place(x=handle_position - 15, y=self.width - 20)

    def value_to_position(self, value):
        padding = self.handle_size // 2
        return padding + (value - self.min_val) / (self.max_val - self.min_val) * (
                self.length - padding * 2
        )

    def position_to_value(self, position):
        padding = self.handle_size // 2
        return (position - padding) / (self.length - padding * 2) * (
                self.max_val - self.min_val
        ) + self.min_val

    def set_value(self, value, update=True):
        curr_value = max(self.min_val, min(self.max_val, value))
        self.value = curr_value
        self.draw_slider()
        if update and self.callback:
            self.callback(self.value)

    def on_click(self, event):
        self.set_value(self.position_to_value(event.x))

    def on_drag(self, event):
        self.set_value(self.position_to_value(event.x))

    def set_bar_fill(self, color):
        self.bar_fill = color
        self.draw_slider()

    def set_bar_outline(self, color):
        self.bar_outline = color
        self.draw_slider()

    def set_handle_fill(self, color):
        self.handle_fill = color
        self.draw_slider()

    def set_background_fill(self, color):
        self.configure(bg=color)
        self.percentage_label.config(bg=color)
        self.draw_slider()

