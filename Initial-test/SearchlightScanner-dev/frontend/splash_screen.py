import tkinter as tk
from PIL import Image, ImageTk
import os
from .application_color_scheme import color_scheme

background_color = color_scheme["colors"]["dark"]["application/window_and_frame_color"]
label_font_color = color_scheme["colors"]["dark"]["label_font_color/fg"]

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, logo_path="logo.png", message="Loading..."):
        super().__init__(parent)
        self.overrideredirect(True)
        self.update_idletasks()

        abs_logo_path = os.path.join(os.path.dirname(__file__), logo_path)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w = int(screen_w * 0.4)
        h = int(screen_h * 0.6)
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        img = Image.open(abs_logo_path)
        max_logo_w = int(w * 0.6)
        max_logo_h = int(h * 0.6)
        img_ratio = img.width / img.height
        box_ratio = max_logo_w / max_logo_h

        if img_ratio > box_ratio:
            new_w = max_logo_w
            new_h = int(max_logo_w / img_ratio)
        else:
            new_h = max_logo_h
            new_w = int(max_logo_h * img_ratio)

        img = img.resize((new_w, new_h), Image.LANCZOS)
        self.logo_img = ImageTk.PhotoImage(img)
        self.logo_label = tk.Label(self, image=self.logo_img, bg=background_color)
        self.logo_label.pack(pady=(20, 10))

        self.label = tk.Label(self, text=message, font=("courier", 14), bg=background_color, fg=label_font_color)
        self.label.pack(pady=(0, 20))

        self.configure(bg=background_color)

    def set_status(self, msg):
        self.label.config(text=msg)
        self.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    splash = SplashScreen(root, logo_path="logo.png", message="Testing Splash Screen...")
    splash.after(1000, lambda: splash.set_status("Still loading..."))
    splash.after(2000, lambda: splash.set_status("Almost done..."))
    
    splash.after(5000, splash.destroy)
    root.mainloop()
