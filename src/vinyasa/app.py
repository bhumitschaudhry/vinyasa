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

from .config import Config
from .camera import Camera
from .tracker import HeadTracker
from .mouse import MouseController
from .ui.calibration import CalibrationWindow

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")

class VinyasaApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        
        self.config = Config.load()
        
        self.root.title(self.config.WINDOW_TITLE)
        self.root.geometry(self.config.WINDOW_SIZE)
        
        self.camera = Camera(camera_id=self.config.CAMERA_ID, fps=self.config.FPS)
        self.tracker = HeadTracker(self.config.MODEL_PATH, self.config.LABELS_PATH)
        self.mouse = MouseController(sensitivity=self.config.INITIAL_SENSITIVITY, 
                                     pause=self.config.DEFAULT_PAUSE, 
                                     failsafe=self.config.FAILSAFE)
        
        self.is_tracking = False
        self.flip_video = True
        
        self.setup_ui()
        self.camera.start()
        self.update_ui()
        
    def setup_ui(self):
        # Main layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        self.header_label = ctk.CTkLabel(self.header_frame, text="VINYASA", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Content area
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Left side: Video feed
        self.video_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right side: Controls
        self.control_panel = ctk.CTkFrame(self.content_frame, width=280, corner_radius=10)
        self.control_panel.grid(row=0, column=1, sticky="nsew")
        
        # Status Frame
        self.status_var = tk.StringVar(value="IDLE")
        self.status_label = ctk.CTkLabel(self.control_panel, textvariable=self.status_var, 
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="gray")
        self.status_label.pack(pady=(20, 5))
        
        self.confidence_var = tk.StringVar(value="Confidence: 0%")
        self.confidence_label = ctk.CTkLabel(self.control_panel, textvariable=self.confidence_var)
        self.confidence_label.pack()
        
        self.prediction_var = tk.StringVar(value="Prediction: -")
        self.prediction_label = ctk.CTkLabel(self.control_panel, textvariable=self.prediction_var)
        self.prediction_label.pack(pady=(0, 20))
        
        # Action Buttons
        self.track_button = ctk.CTkButton(self.control_panel, text="START TRACKING", 
                                         command=self.toggle_tracking, font=ctk.CTkFont(weight="bold"))
        self.track_button.pack(fill=tk.X, padx=20, pady=5)
        
        self.calibrate_button = ctk.CTkButton(self.control_panel, text="CALIBRATE", 
                                             fg_color="transparent", border_width=2,
                                             command=self.open_calibration)
        self.calibrate_button.pack(fill=tk.X, padx=20, pady=5)

        self.flip_button = ctk.CTkButton(self.control_panel, text="FLIP VIEW", 
                                        fg_color="transparent", border_width=2,
                                        command=self.toggle_flip)
        self.flip_button.pack(fill=tk.X, padx=20, pady=5)
        
        # Settings
        ctk.CTkLabel(self.control_panel, text="Sensitivity", font=ctk.CTkFont(size=12)).pack(pady=(20, 0))
        self.sensitivity_scale = ctk.CTkSlider(self.control_panel, from_=1, to=50, command=self.update_sensitivity)
        self.sensitivity_scale.set(self.config.INITIAL_SENSITIVITY)
        self.sensitivity_scale.pack(fill=tk.X, padx=20, pady=5)
        
        ctk.CTkLabel(self.control_panel, text="Confidence Threshold", font=ctk.CTkFont(size=12)).pack(pady=(10, 0))
        self.threshold_scale = ctk.CTkSlider(self.control_panel, from_=0.5, to=0.99, command=self.update_threshold)
        self.threshold_scale.set(self.config.CONFIDENCE_THRESHOLD)
        self.threshold_scale.pack(fill=tk.X, padx=20, pady=5)

        # Footer
        self.footer = ctk.CTkLabel(self.root, text="Hotkey: F10 to Toggle Tracking", font=ctk.CTkFont(size=10))
        self.footer.grid(row=2, column=0, pady=10)

        # Hotkeys
        self.root.bind("<F10>", lambda e: self.toggle_tracking())
        
    def toggle_tracking(self):
        self.is_tracking = not self.is_tracking
        if self.is_tracking:
            self.track_button.configure(text="STOP TRACKING", fg_color="#db3d3d", hover_color="#be3939")
            self.status_var.set("RUNNING")
            self.status_label.configure(text_color="#47dd47")
            self.tracking_thread = threading.Thread(target=self.track_loop, daemon=True)
            self.tracking_thread.start()
        else:
            self.track_button.configure(text="START TRACKING", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#367E96", "#145173"])
            self.status_var.set("IDLE")
            self.status_label.configure(text_color="gray")
            
    def toggle_flip(self):
        self.flip_video = not self.flip_video

    def open_calibration(self):
        CalibrationWindow(self.root, self.config, self.mouse)
        
    def update_sensitivity(self, value):
        self.mouse.set_sensitivity(value)
        self.config.INITIAL_SENSITIVITY = int(value)

    def update_threshold(self, value):
        self.config.CONFIDENCE_THRESHOLD = float(value)
        
    def track_loop(self):
        prediction_history = []
        history_size = 3
        while self.is_tracking:
            ret, frame = self.camera.read()
            if ret:
                label, confidence = self.tracker.predict(frame)
                prediction_history.append(label)
                if len(prediction_history) > history_size:
                    prediction_history.pop(0)
                smoothed_label = max(set(prediction_history), key=prediction_history.count)
                
                self.confidence_var.set(f"Confidence: {int(confidence*100)}%")
                self.prediction_var.set(f"Prediction: {smoothed_label}")
                
                if confidence >= self.config.CONFIDENCE_THRESHOLD:
                    self.mouse.execute_command(smoothed_label)
            time.sleep(0.01)
            
    def update_ui(self):
        ret, frame = self.camera.read()
        if ret:
            if self.flip_video:
                frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            
            # Dynamic resizing
            width = self.video_frame.winfo_width() - 10
            height = self.video_frame.winfo_height() - 10
            if width > 0 and height > 0:
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
