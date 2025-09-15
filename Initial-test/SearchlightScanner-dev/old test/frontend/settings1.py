import tkinter as tk
from tkinter import font as tkFont
from tkinter import ttk

from .shared_confidence_controller import shared_confidence
from .application_current_settings_route import current_settings_route
from constants.constantsmanager import ConstantsManager


# Custom slider class
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


# Settings frame with custom sliders
class SettingsFrame1(tk.Frame):
    def __init__(self, parent, camera_feed_1, camera_feed_2, application, color_scheme, **kwargs):
        super().__init__(parent, **kwargs)
        self.constants_manager = ConstantsManager(filename=current_settings_route)
        self.application = application
        self.color_scheme = color_scheme
        self.focus_mode = tk.StringVar(value="Automatic")
        shared_confidence.register_observer(self.update_confidence)
        self.camera_feed_1 = camera_feed_1
        self.camera_feed_2 = camera_feed_2
        self.current_cam = tk.IntVar(value=0)
        self.style = ttk.Style()
        self.default_settings_pushed = True
        self.create_widgets()
        self.update_colors()

    def update_colors(self):
        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        color_scheme = self.color_scheme["colors"][mode]

        self.configure(bg=color_scheme["application/window_and_frame_color"])
        self.sliders_frame.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.confidence_frame.configure(
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

        self.cam_select_buttons_frame.configure(
            bg=color_scheme["application/window_and_frame_color"]
        )
        self.cam_select_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )

        if self.current_cam.get() == 0:
            self.camera_one_button.configure(
                bg=(
                    color_scheme["focus_button_bg_dark_active"]
                    if mode == "dark"
                    else color_scheme["focus_button_bg_light_active"]
                )
            )
            self.camera_two_button.configure(
                bg=(
                    color_scheme["focus_button_bg_dark_inactive"]
                    if mode == "dark"
                    else color_scheme["focus_button_bg_light_inactive"]
                )
            )
        else:
            self.camera_one_button.configure(
                bg=(
                    color_scheme["focus_button_bg_dark_inactive"]
                    if mode == "dark"
                    else color_scheme["focus_button_bg_light_inactive"]
                )
            )
            self.camera_two_button.configure(
                bg=(
                    color_scheme["focus_button_bg_dark_active"]
                    if mode == "dark"
                    else color_scheme["focus_button_bg_light_active"]
                )
            )

        self.darkmode_toggle_frame.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.darkmode_toggle_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )

        self.darkmode_toggle_canvas.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.settings1_button.configure(bg=color_scheme["selected_color"])
        self.settings2_button.configure(bg=color_scheme["unselected_settings_button"])

        self.resolution_frame_and_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.resolution_label.configure(
            bg=color_scheme["application/window_and_frame_color"],
            fg=color_scheme["label_font_color/fg"],
        )

        self.resolutions_frame.configure(
            bg=color_scheme["button_bg"],
            highlightbackground=color_scheme["frame_outline_color"],
            highlightcolor=color_scheme["frame_outline_color"],
        )

        self.close_menu_button.configure(bg=color_scheme["apply_changes_background"])

        # Update the styles for TMenubutton and TMenu
        self.style.map(
            "TMenubutton",
            background=[
                ("active", color_scheme["selected_color"]),
                ("!active", color_scheme["button_bg"]),
            ],
            foreground=[
                ("active", color_scheme["button_font_color/fg"]),
                ("!active", color_scheme["button_font_color/fg"]),
            ],
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

        if self.default_settings_pushed == True:
            self.default_settings_button.configure(bg=color_scheme["selected_color"])
            self.custom_settings_button.configure(
                bg=color_scheme["settings_select_buttons_inactive"]
            )
        else:
            self.default_settings_button.configure(
                bg=color_scheme["settings_select_buttons_inactive"]
            )
            self.custom_settings_button.configure(bg=color_scheme["selected_color"])

        self.open_notes_button.configure(
            bg=color_scheme["settings_select_buttons_inactive"]
        )

        self.save_button.configure(bg=color_scheme["selected_color"])

        self.open_comments_button.configure(
            bg=color_scheme["settings_select_buttons_inactive"]
        )

        self.save_comments_button.configure(bg=color_scheme["selected_color"])

    def update_confidence(self, value):
        # This method updates the slider's position and the label's text
        self.confidence_slider.set_value(value, update=False)  # Update the slider
        self.confidence_label.config(
            text=f"CONFIDENCE: {int(round(value))}%"
        )  # Update the label

    def toggle_darkmode_switch(
            self, switch_canvas, switch_background, switch_indicator, switch_state
    ):
        switch_state["is_on"] = not switch_state["is_on"]

        if switch_state["is_on"]:
            switch_canvas.itemconfig(switch_background, fill="#006400")
            switch_canvas.coords(switch_indicator, 60, 10, 90, 40)
            self.update_colors()
        else:
            switch_canvas.itemconfig(switch_background, fill="#697283")
            switch_canvas.coords(switch_indicator, 10, 10, 40, 40)

        # Call the method on the Application class to update all frames
        self.application.toggle_dark_mode()

    def select_camera(self, cam_index):
        if cam_index == 0:
            self.camera_feed_1.change_camera(self.constants_manager.get_constant("camera_feed_1"))
        else:
            self.camera_feed_2.change_camera(self.constants_manager.get_constant("camera_feed_2"))
        self.current_cam.set(cam_index)
        self.update_camera_selection()

    def update_camera_selection(self):
        self.camera_one_status.config(
            text="(Connected)" if self.camera_feed_1.is_connected() else "(Not Connected)"
        )
        self.camera_two_status.config(
            text="(Connected)" if self.camera_feed_2.is_connected() else "(Not Connected)"
        )

        self.camera_one_status.config(
            text="(Connected)" if self.camera_feed_1.is_connected() else "(Not Connected)"
        )
        self.camera_two_status.config(
            text="(Connected)" if self.camera_feed_2.is_connected() else "(Not Connected)"
        )

    def on_slider_change(self, value):
        from .shared_confidence_controller import shared_confidence

        shared_confidence.set_value(value)

    def selection_changed(self, value):
        self.constants_manager.set_constant("default_resolution", value)
        print("Selected:", value)
        res = value.split()[0].split("x")
        self.camera_feed.change_resolution(res[0], res[1])

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

    def create_widgets(self):
        font_used = tkFont.Font(family="Helvetica", size=14, weight="bold")  # Increased font size

        container = tk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        mode = "dark" if self.color_scheme["dark_mode"] else "light"
        bg_color = self.color_scheme["colors"][mode]["application/window_and_frame_color"]
        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0, bg=bg_color)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.sliders_frame = tk.Frame(canvas)

        self.sliders_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sliders_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.confidence_frame = tk.Frame(
            self.sliders_frame, width=900, height=200, bg="#7C889C",
            highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.confidence_frame.grid(row=0, column=0, padx=10, pady=20)
        self.confidence_frame.grid_propagate(False)

        self.confidence_label = tk.Label(
            self.confidence_frame, text="CONFIDENCE: 0%", bg="#7C889C", fg="black", font=font_used)
        self.confidence_label.grid(row=0, column=0, sticky="nsew")

        self.confidence_slider = CustomSlider(
            self.confidence_frame, id="confidence_slider", length=800, width=140,
            handle_size=70, bar_thickness=70, bg="#7C889C", min_val=0, max_val=100,
            callback=self.on_slider_change)
        self.confidence_slider.grid(row=1, column=0, padx=5)

        self.resolution_frame_and_label = tk.Frame(
            self.sliders_frame, bg="#7C889C", highlightbackground="black",
            highlightcolor="black", highlightthickness=2, width=900, height=200)
        self.resolution_frame_and_label.grid(row=2, column=0, padx=10, pady=20, sticky="ew")
        self.resolution_frame_and_label.grid_propagate(False)

        self.resolution_label = tk.Label(
            self.resolution_frame_and_label, text="SELECT RESOLUTION", bg="#7C889C",
            fg="black", font=font_used)
        self.resolution_label.grid(row=0, column=0, sticky="ew")

        self.resolutions_frame = tk.Frame(
            self.resolution_frame_and_label, bg="#7C889C", highlightbackground="black",
            highlightcolor="black", highlightthickness=2, width=900, height=120)
        self.resolutions_frame.grid(row=1, column=0, sticky="ew")

        menu_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        frame = tk.Frame(self.resolutions_frame, bg="darkgrey")
        frame.pack(padx=10, pady=10)
        selected_option = tk.StringVar(value="1920x1080 pixels")
        options = ["1280x720 pixels", "1920x1080 pixels", "2560x1440 pixels", "3840x2160 pixels"]
        self.option_menu = ttk.OptionMenu(
            frame, selected_option, selected_option.get(), *options, command=self.selection_changed)
        self.option_menu.pack(expand=True, fill="both")
        self.style.configure("TMenubutton", font=menu_font, width=60, height=40)
        menu = self.option_menu["menu"]
        menu.config(font=menu_font)

        self.settings_select_buttons_frame = tk.Frame(self.sliders_frame, bg="#7C889C", width=800, height=120)
        self.settings_select_buttons_frame.grid(row=3, column=0, padx=10, pady=10)

        self.default_settings_button = tk.Button(
            self.settings_select_buttons_frame, text="DEFAULT SETTINGS", bg="#24D215",
            fg="white", font=font_used, width=25, height=3, command=self.default_setings_selection)
        self.default_settings_button.grid(row=0, column=0)

        self.custom_settings_button = tk.Button(
            self.settings_select_buttons_frame, text="CUSTOM SETTINGS", bg="grey",
            fg="white", font=font_used, width=25, height=3, command=self.custom_settings_selection)
        self.custom_settings_button.grid(row=0, column=1)

        self.open_notes_button = tk.Button(
            self.sliders_frame, text="OPEN OPERATOR NOTES", bg="grey", fg="white",
            font=font_used, width=25, height=3, command=self.show_operator_notes)
        self.open_notes_button.grid(row=4, column=0, padx=10, pady=10)

        self.text_field_frame = tk.Frame(
            self, bg="black", height=600, width=1800,
            highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.text_field = tk.Text(
            self.text_field_frame, bg="white", font=("Helvetica", 14), fg="black",
            height=28, width=150)
        self.text_field.place(x=0, y=0)
        self.text_field.insert("1.0", self.constants_manager.get_constant("operator_notes"))
        self.save_button = tk.Button(
            self.text_field_frame, text="SAVE", bg="#24D215", fg="white", font=font_used,
            height=2, width=25, command=self.save_notes_input)
        self.save_button.place(relx=0.85, rely=0.9, anchor="se")

        self.open_comments_button = tk.Button(
            self.sliders_frame, text="OPEN OPERATOR COMMENTS", bg="grey", fg="white",
            font=font_used, width=30, height=3, command=self.show_operator_comments)
        self.open_comments_button.grid(row=5, column=0, padx=10, pady=10)

        self.comments_text_field_frame = tk.Frame(
            self, bg="black", height=600, width=1800,
            highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.comments_text_field = tk.Text(
            self.comments_text_field_frame, bg="white", font=("Helvetica", 14), fg="black",
            height=28, width=150)
        self.comments_text_field.place(x=0, y=0)
        self.comments_text_field.insert("1.0", self.constants_manager.get_constant("operator_comments"))
        self.save_comments_button = tk.Button(
            self.comments_text_field_frame, text="SAVE COMMENTS", bg="#24D215", fg="white",
            font=font_used, height=2, width=25, command=self.save_comments_input)
        self.save_comments_button.place(relx=0.85, rely=0.9, anchor="se")

        self.cam_select_buttons_frame = tk.Frame(self.sliders_frame, bg="#7C889C", width=900, height=150)
        self.cam_select_buttons_frame.grid(row=6, column=0, padx=10, pady=10)

        self.cam_select_label = tk.Label(
            self.cam_select_buttons_frame, text="SELECT CAMERA INPUT", bg="#7C889C",
            fg="black", font=font_used)
        self.cam_select_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.camera_one_button = tk.Button(
            self.cam_select_buttons_frame, text="CAMERA 1", bg="#24D215", fg="white",
            font=font_used, width=25, height=3, command=lambda: self.set_camera_mode("camera1"))
        self.camera_one_button.grid(row=1, column=0)

        self.camera_one_status = tk.Label(
            self.cam_select_buttons_frame,
            text="(Connected)" if self.camera_feed_1.is_connected() else "(Not Connected)",
            bg="#7C889C", fg="black", font=("Helvetica", 10, "italic"))
        self.camera_one_status.grid(row=2, column=0)

        self.camera_two_button = tk.Button(
            self.cam_select_buttons_frame, text="CAMERA 2", bg="grey", fg="white",
            font=font_used, width=25, height=3, command=lambda: self.set_camera_mode("camera2"))
        self.camera_two_button.grid(row=1, column=1)

        self.camera_two_status = tk.Label(
            self.cam_select_buttons_frame,
            text="(Connected)" if self.camera_feed_2.is_connected() else "(Not Connected)",
            bg="#7C889C", fg="black", font=("Helvetica", 10, "italic"))
        self.camera_two_status.grid(row=2, column=1)

        self.split_view_button = tk.Button(
            self.cam_select_buttons_frame, text="SPLIT VIEW", bg="grey", fg="white",
            font=font_used, width=20, height=3,
            command=lambda: self.set_camera_mode("split"))
        self.split_view_button.grid(row=1, column=2)

        self.darkmode_toggle_frame = tk.Frame(
            self.sliders_frame, bg="#7C889C", highlightbackground="black",
            highlightcolor="black", highlightthickness=2, width=500, height=160)
        self.darkmode_toggle_frame.grid(row=7, column=0, padx=10, pady=10)

        self.darkmode_toggle_label = tk.Label(
            self.darkmode_toggle_frame, text="DARK MODE", bg="#7C889C", fg="black",
            font=font_used)
        self.darkmode_toggle_label.place(x=40, y=60)

        darkmode_switch_state = {"is_on": False}
        self.darkmode_toggle_canvas = tk.Canvas(
            self.darkmode_toggle_frame, width=120, height=60, bg="#7C889C",
            highlightthickness=0, highlightbackground="black", highlightcolor="black")
        self.darkmode_toggle_canvas.place(x=300, y=50)
        self.darkmode_switch_background = self.darkmode_toggle_canvas.create_rectangle(
            5, 10, 115, 50, fill="#697283")
        darkmode_switch = self.darkmode_toggle_canvas.create_oval(
            10, 10, 50, 50, outline="black", fill="white")
        self.darkmode_toggle_canvas.tag_bind(
            darkmode_switch, "<Button-1>",
            lambda event: self.toggle_darkmode_switch(
                self.darkmode_toggle_canvas, self.darkmode_switch_background,
                darkmode_switch, darkmode_switch_state))

        self.settings_toggle_frame = tk.Frame(self, width=120, height=120)
        self.settings_toggle_frame.grid(row=1, column=0, padx=10, pady=20, sticky="w")

        self.settings1_button = tk.Button(
            self.settings_toggle_frame, command=self.master.switch_settings1,
            text="SETTINGS 1", bg="#24D215", fg="white", font=font_used, width=30, height=5)
        self.settings1_button.grid(row=0, column=0, sticky="ew")

        self.settings2_button = tk.Button(
            self.settings_toggle_frame, command=self.master.switch_settings2,
            text="SETTINGS 2", bg="#555", fg="white", font=font_used, width=30, height=5)
        self.settings2_button.grid(row=0, column=1, sticky="ew")

        self.close_menu_button_frame = tk.Frame(
            self, highlightbackground="black", highlightcolor="black",
            highlightthickness=2, width=60, height=60)
        self.close_menu_button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        self.close_menu_button_frame.grid_propagate(False)
        x_button_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
        self.close_menu_button = tk.Button(
            self.close_menu_button_frame, text="X", bg="red", fg="white",
            font=x_button_font, command=self.master.switch_main_frame)
        self.close_menu_button.pack(ipadx=5, ipady=5, expand=True)

        #############################################################################################################

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

        if mode == "camera1":
            self.current_cam.set(0)
        elif mode == "camera2":
            self.current_cam.set(1)
        else:
            self.current_cam.set(2)

            # Refresh button colors based on current selection
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

        self.camera_one_button.configure(
            bg=active if cam_mode == "camera1" else inactive
        )
        self.camera_two_button.configure(
            bg=active if cam_mode == "camera2" else inactive
        )
        self.split_view_button.configure(
            bg=active if cam_mode == "split" else inactive
        )


