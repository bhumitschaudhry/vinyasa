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

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VinyasaApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.config = Config.load()
        
        # Window Setup
        self.root.title(self.config.WINDOW_TITLE)
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
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
        # Configure grid layout (1x2)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="VINYASA", 
                                        font=ctk.CTkFont(size=26, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.subtitle_label = ctk.CTkLabel(self.sidebar_frame, text="Head Tracking Mouse", 
                                            font=ctk.CTkFont(size=12), text_color="gray")
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Action Buttons
        self.track_button = ctk.CTkButton(self.sidebar_frame, text="START ENGINE", 
                                         height=45, corner_radius=8,
                                         command=self.toggle_tracking, 
                                         font=ctk.CTkFont(weight="bold"))
        self.track_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.calibrate_button = ctk.CTkButton(self.sidebar_frame, text="CALIBRATION WIZARD", 
                                             height=40, corner_radius=8,
                                             fg_color="transparent", border_width=2,
                                             command=self.open_calibration)
        self.calibrate_button.grid(row=3, column=0, padx=20, pady=10)

        self.flip_button = ctk.CTkButton(self.sidebar_frame, text="FLIP CAMERA VIEW", 
                                        height=40, corner_radius=8,
                                        fg_color="transparent", border_width=2,
                                        command=self.toggle_flip)
        self.flip_button.grid(row=4, column=0, padx=20, pady=10)
        
        # Appearance Controls
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(30, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        # Info Section at bottom
        self.hotkey_label = ctk.CTkLabel(self.sidebar_frame, text="HOTKEY: F10", 
                                         font=ctk.CTkFont(size=10, weight="bold"),
                                         text_color="gray60")
        self.hotkey_label.grid(row=9, column=0, padx=20, pady=20)

        # --- MAIN CONTENT ---
        self.main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)

        # Top Bar: Status & Info
        self.top_bar = ctk.CTkFrame(self.main_content, height=80, corner_radius=12)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Status
        self.status_container = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.status_container.pack(side=tk.LEFT, padx=30)
        
        self.status_val_var = tk.StringVar(value="SYSTEM IDLE")
        self.status_label = ctk.CTkLabel(self.status_container, textvariable=self.status_val_var, 
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        text_color="gray60")
        self.status_label.pack(side=tk.LEFT)

        # Telemetry
        self.telemetry_container = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.telemetry_container.pack(side=tk.RIGHT, padx=30)

        self.confidence_var = tk.StringVar(value="CONFIDENCE: 0%")
        self.confidence_label = ctk.CTkLabel(self.telemetry_container, textvariable=self.confidence_var,
                                              font=ctk.CTkFont(family="Courier", size=13))
        self.confidence_label.pack(side=tk.LEFT, padx=20)
        
        self.prediction_var = tk.StringVar(value="ACTION: NONE")
        self.prediction_label = ctk.CTkLabel(self.telemetry_container, textvariable=self.prediction_var,
                                              font=ctk.CTkFont(family="Courier", size=13, weight="bold"))
        self.prediction_label.pack(side=tk.LEFT)

        # Middle Area: Camera and Settings
        self.middle_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.middle_frame.grid(row=1, column=0, sticky="nsew")
        self.middle_frame.grid_columnconfigure(0, weight=3)
        self.middle_frame.grid_columnconfigure(1, weight=1)
        self.middle_frame.grid_rowconfigure(0, weight=1)

        # Video Frame
        self.video_container = ctk.CTkFrame(self.middle_frame, corner_radius=12, border_width=2, border_color="#333333")
        self.video_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        self.video_label = ctk.CTkLabel(self.video_container, text="CAMERA INACTIVE", text_color="#444444")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Settings Panel
        self.settings_panel = ctk.CTkFrame(self.middle_frame, corner_radius=12)
        self.settings_panel.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.settings_panel, text="ENGINE SETTINGS", 
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(25, 20))
        
        # Sensitivity
        ctk.CTkLabel(self.settings_panel, text="Sensitivity", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=25)
        self.sensitivity_scale = ctk.CTkSlider(self.settings_panel, from_=1, to=50, number_of_steps=49,
                                               command=self.update_sensitivity)
        self.sensitivity_scale.set(self.config.INITIAL_SENSITIVITY)
        self.sensitivity_scale.pack(fill=tk.X, padx=25, pady=(5, 20))
        
        # Confidence
        ctk.CTkLabel(self.settings_panel, text="Confidence Threshold", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=25)
        self.threshold_scale = ctk.CTkSlider(self.settings_panel, from_=0.5, to=0.99, 
                                               command=self.update_threshold)
        self.threshold_scale.set(self.config.CONFIDENCE_THRESHOLD)
        self.threshold_scale.pack(fill=tk.X, padx=25, pady=(5, 20))

        # Save Settings
        self.save_cfg_btn = ctk.CTkButton(self.settings_panel, text="SAVE PERMANENTLY", 
                                          height=32, corner_radius=6,
                                          fg_color="#2b2b2b", hover_color="#3b3b3b",
                                          command=self.config.save)
        self.save_cfg_btn.pack(side=tk.BOTTOM, pady=25, padx=25, fill=tk.X)

        # Hotkeys
        self.root.bind("<F10>", lambda e: self.toggle_tracking())
        
    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def toggle_tracking(self):
        self.is_tracking = not self.is_tracking
        if self.is_tracking:
            self.track_button.configure(text="STOP ENGINE", fg_color="#db3d3d", hover_color="#be3939")
            self.status_val_var.set("SYSTEM RUNNING")
            self.status_label.configure(text_color="#47dd47")
            self.tracking_thread = threading.Thread(target=self.track_loop, daemon=True)
            self.tracking_thread.start()
        else:
            self.track_button.configure(text="START ENGINE", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#367E96", "#145173"])
            self.status_val_var.set("SYSTEM IDLE")
            self.status_label.configure(text_color="gray60")
            
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
                
                self.confidence_var.set(f"CONFIDENCE: {int(confidence*100)}%")
                self.prediction_var.set(f"ACTION: {smoothed_label.upper()}")
                
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
            width = self.video_container.winfo_width() - 4
            height = self.video_container.winfo_height() - 4
            if width > 100 and height > 100:
                img = img.resize((width, height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image=img)
                self.video_label.configure(image=photo, text="")
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
