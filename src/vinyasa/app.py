import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import queue
import time
import logging
import sys
import os

from .config import Config
from .camera import Camera
from .tracker import HeadTracker
from .mouse import MouseController
from .ui.calibration import CalibrationWindow

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure CustomTkinter for Light Theme as per mockup
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class VinyasaApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.config = Config.load()
        
        # Window Setup
        self.root.title(self.config.WINDOW_TITLE)
        self.root.geometry(self.config.WINDOW_SIZE)
        self.root.configure(fg_color="#F0F0F0") # Light grey background for the window shadow effect

        # Load Logo
        self.logo_path = os.path.join(os.getcwd(), "vinyasa-logo.png")
        self.logo_image = None
        if os.path.exists(self.logo_path):
            self.logo_image = ctk.CTkImage(light_image=Image.open(self.logo_path),
                                         dark_image=Image.open(self.logo_path),
                                         size=(120, 40))
        
        # Components
        self.camera = Camera(camera_id=self.config.CAMERA_ID, fps=self.config.FPS)
        self.tracker = HeadTracker(self.config.MODEL_PATH, self.config.LABELS_PATH)
        self.mouse = MouseController(sensitivity=self.config.INITIAL_SENSITIVITY, 
                                     pause=self.config.DEFAULT_PAUSE, 
                                     failsafe=self.config.FAILSAFE)
        
        # State
        self.is_tracking = False
        self.flip_video = True
        
        self.setup_ui()
        self.camera.start()
        self.update_ui()
        
    def setup_ui(self):
        # Main Container (White Rounded Card)
        self.main_container = ctk.CTkFrame(self.root, fg_color="white", corner_radius=25)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Traffic Light Buttons (Top Right)
        self.traffic_lights = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.traffic_lights.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        colors = ["#FF605C", "#FFBD44", "#00CA4E"] # Red, Yellow, Green
        for color in colors:
            btn = ctk.CTkLabel(self.traffic_lights, text="", fg_color=color, width=12, height=12, corner_radius=6)
            btn.pack(side=tk.LEFT, padx=3)

        # Content Layout
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(60, 40))
        
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDE: Video Feed ---
        self.video_container = ctk.CTkFrame(self.content_frame, fg_color="#F9D448", corner_radius=20) # Yellow background as per mockup
        self.video_container.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        
        self.video_label = ctk.CTkLabel(self.video_container, text="")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # --- RIGHT SIDE: Settings ---
        self.settings_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_container.grid(row=0, column=1, sticky="nsew")
        
        self.settings_label = ctk.CTkLabel(self.settings_container, text="Settings", 
                                           font=ctk.CTkFont(size=24, weight="bold"),
                                           text_color="black")
        self.settings_label.pack(anchor="w", pady=(0, 30))

        # Sliders
        self.create_slider("Mouse Sensitivity", self.config.INITIAL_SENSITIVITY, 1, 100, self.update_sensitivity)
        self.create_slider("Lines per second", self.config.LINES_PER_SECOND, 1, 10, self.update_lps)
        self.create_slider("Cursor Size", self.config.CURSOR_SIZE, 1, 5, self.update_cursor_size)

        # Start/Stop Button (Added for functionality as it's not in mockup)
        self.track_button = ctk.CTkButton(self.settings_container, text="Start Tracking", 
                                         command=self.toggle_tracking,
                                         corner_radius=10, height=40,
                                         fg_color="#3B8ED0", hover_color="#367E96")
        self.track_button.pack(fill=tk.X, pady=(30, 0))

        # Logo (Bottom Right)
        if self.logo_image:
            self.logo_display = ctk.CTkLabel(self.main_container, image=self.logo_image, text="")
            self.logo_display.place(relx=1.0, rely=1.0, anchor="se", x=-40, y=-30)

    def create_slider(self, label, value, from_, to, command):
        frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        frame.pack(fill=tk.X, pady=10)
        
        lbl = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12), text_color="black")
        lbl.pack(anchor="w")
        
        slider = ctk.CTkSlider(frame, from_=from_, to=to, number_of_steps=to-from_, 
                               command=command, height=16, 
                               button_color="#3B8ED0", progress_color="#3B8ED0")
        slider.set(value)
        slider.pack(fill=tk.X, pady=(5, 0))

    def toggle_tracking(self):
        self.is_tracking = not self.is_tracking
        if self.is_tracking:
            self.track_button.configure(text="Stop Tracking", fg_color="#FF605C", hover_color="#be3939")
            self.tracking_thread = threading.Thread(target=self.track_loop, daemon=True)
            self.tracking_thread.start()
        else:
            self.track_button.configure(text="Start Tracking", fg_color="#3B8ED0", hover_color="#367E96")
            
    def update_sensitivity(self, value):
        self.mouse.set_sensitivity(value)
        self.config.INITIAL_SENSITIVITY = int(value)

    def update_lps(self, value):
        self.config.LINES_PER_SECOND = int(value)

    def update_cursor_size(self, value):
        self.config.CURSOR_SIZE = int(value)

    def track_loop(self):
        while self.is_tracking:
            ret, frame = self.camera.read()
            if ret:
                label, confidence = self.tracker.predict(frame)
                if confidence >= self.config.CONFIDENCE_THRESHOLD:
                    self.mouse.execute_command(label)
            time.sleep(0.01)
            
    def update_ui(self):
        ret, frame = self.camera.read()
        if ret:
            if self.flip_video:
                frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            
            # Match the aspect ratio and rounding of the mockup
            width = self.video_container.winfo_width()
            height = self.video_container.winfo_height()
            if width > 100 and height > 100:
                img = img.resize((width, height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)
                self.video_label.configure(image=photo)
                self.video_label.image = photo
            
        self.root.after(30, self.update_ui)
        
    def on_closing(self):
        self.is_tracking = False
        self.config.save()
        self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    app_root = ctk.CTk()
    app = VinyasaApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app_root.mainloop()
