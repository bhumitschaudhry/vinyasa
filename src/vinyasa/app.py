import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import queue
import time
import logging

from .config import Config
from .camera import Camera
from .tracker import HeadTracker
from .mouse import MouseController
from .ui.calibration import CalibrationWindow

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VinyasaApp:
    def __init__(self, root: tk.Tk):
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
        self.prediction_queue = queue.Queue(maxsize=1)
        
        self.setup_ui()
        self.camera.start()
        self.update_ui()
        
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Status.TLabel", font=("Helvetica", 12))

        # Main layout
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(self.main_frame, text="Vinyasa Head Tracker", style="Header.TLabel")
        header.pack(fill=tk.X, pady=(0, 15))

        # Content area
        content = ttk.Frame(self.main_frame)
        content.pack(fill=tk.BOTH, expand=True)

        # Left side: Video feed
        self.video_frame = ttk.LabelFrame(content, text="Live Camera Feed", padding=5)
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Right side: Controls
        self.control_panel = ttk.Frame(content, width=280)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.control_panel.pack_propagate(False)
        
        # Status Frame
        self.status_frame = ttk.LabelFrame(self.control_panel, text="System Status", padding="10")
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="IDLE")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack()
        
        self.confidence_var = tk.StringVar(value="Confidence: 0%")
        self.confidence_label = ttk.Label(self.status_frame, textvariable=self.confidence_var)
        self.confidence_label.pack(pady=(5, 0))
        
        self.prediction_var = tk.StringVar(value="Prediction: -")
        self.prediction_label = ttk.Label(self.status_frame, textvariable=self.prediction_var)
        self.prediction_label.pack()
        
        # Action Frame
        self.action_frame = ttk.LabelFrame(self.control_panel, text="Operations", padding="10")
        self.action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.track_button = ttk.Button(self.action_frame, text="▶ START TRACKING", command=self.toggle_tracking)
        self.track_button.pack(fill=tk.X, pady=4)
        
        self.calibrate_button = ttk.Button(self.action_frame, text="⚙ CALIBRATE", command=self.open_calibration)
        self.calibrate_button.pack(fill=tk.X, pady=4)

        self.flip_button = ttk.Button(self.action_frame, text="↔ FLIP VIEW", command=self.toggle_flip)
        self.flip_button.pack(fill=tk.X, pady=4)
        
        # Settings Frame
        self.settings_frame = ttk.LabelFrame(self.control_panel, text="Quick Settings", padding="10")
        self.settings_frame.pack(fill=tk.X)
        
        ttk.Label(self.settings_frame, text="Sensitivity").pack(anchor=tk.W)
        self.sensitivity_scale = ttk.Scale(self.settings_frame, from_=1, to=50, orient=tk.HORIZONTAL, command=self.update_sensitivity)
        self.sensitivity_scale.set(self.config.INITIAL_SENSITIVITY)
        self.sensitivity_scale.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.settings_frame, text="Confidence Min").pack(anchor=tk.W)
        self.threshold_scale = ttk.Scale(self.settings_frame, from_=0.5, to=0.99, orient=tk.HORIZONTAL, command=self.update_threshold)
        self.threshold_scale.set(self.config.CONFIDENCE_THRESHOLD)
        self.threshold_scale.pack(fill=tk.X)

        # Hotkeys
        self.root.bind("<F10>", lambda e: self.toggle_tracking())
        
        # Footer / Info
        self.footer = ttk.Label(self.main_frame, text="Hotkey: F10 to Toggle Tracking", font=("Helvetica", 8))
        self.footer.pack(side=tk.BOTTOM, pady=(10, 0))
        
    def toggle_tracking(self):
        self.is_tracking = not self.is_tracking
        if self.is_tracking:
            self.track_button.config(text="■ STOP TRACKING")
            self.status_var.set("RUNNING")
            self.status_label.config(foreground="green")
            # Start tracking thread
            self.tracking_thread = threading.Thread(target=self.track_loop, daemon=True)
            self.tracking_thread.start()
        else:
            self.track_button.config(text="▶ START TRACKING")
            self.status_var.set("IDLE")
            self.status_label.config(foreground="black")
            
    def toggle_flip(self):
        self.flip_video = not self.flip_video

    def open_calibration(self):
        CalibrationWindow(self.root, self.config, self.mouse)
        
    def update_sensitivity(self, value):
        self.mouse.set_sensitivity(value)
        self.config.INITIAL_SENSITIVITY = int(float(value))

    def update_threshold(self, value):
        self.config.CONFIDENCE_THRESHOLD = float(value)
        
    def track_loop(self):
        prediction_history = []
        history_size = 3

        while self.is_tracking:
            ret, frame = self.camera.read()
            if ret:
                label, confidence = self.tracker.predict(frame)
                
                # Prediction smoothing
                prediction_history.append(label)
                if len(prediction_history) > history_size:
                    prediction_history.pop(0)
                
                # Get the most common label in recent history
                smoothed_label = max(set(prediction_history), key=prediction_history.count)
                
                # Update UI info
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
            
            # Convert to RGB and then to PhotoImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            
            # Resize for display
            width, height = 540, 400
            img = img.resize((width, height), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
        self.root.after(30, self.update_ui)
        
    def on_closing(self):
        self.is_tracking = False
        self.config.save()
        self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VinyasaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
