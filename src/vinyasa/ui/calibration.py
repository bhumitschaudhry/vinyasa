import tkinter as tk
from tkinter import ttk

class CalibrationWindow(tk.Toplevel):
    def __init__(self, parent, config, mouse_controller):
        super().__init__(parent)
        self.title("Calibration Wizard")
        self.geometry("400x300")
        self.config = config
        self.mouse = mouse_controller
        
        self.setup_ui()
        
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.configure("Bold.TLabel", font=("Helvetica", 10, "bold"))

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Calibration Wizard", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        
        self.info_text = tk.StringVar(value="Move your head to the extremes to test sensitivity. Adjust the sliders below to your comfort.")
        ttk.Label(main_frame, textvariable=self.info_text, wraplength=350).pack(pady=(0, 20))
        
        # Directions sensitivity
        sens_frame = ttk.LabelFrame(main_frame, text="Movement Settings", padding="10")
        sens_frame.pack(fill=tk.X, expand=True)
        
        ttk.Label(sens_frame, text="Current Sensitivity:", style="Bold.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sens_val_label = ttk.Label(sens_frame, text=f"{int(self.mouse.sensitivity)}")
        self.sens_val_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(sens_frame, text="Adjust Range:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.sens_scale = ttk.Scale(sens_frame, from_=1, to=100, orient=tk.HORIZONTAL, command=self.on_sens_change)
        self.sens_scale.set(self.mouse.sensitivity)
        self.sens_scale.grid(row=1, column=1, sticky=tk.EW, padx=5)
        
        sens_frame.columnconfigure(1, weight=1)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Save Calibration", command=self.save_and_close).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=10)

    def on_sens_change(self, value):
        self.sens_val_label.config(text=f"{int(float(value))}")
        
    def save_and_close(self):
        new_sens = int(float(self.sens_scale.get()))
        self.mouse.set_sensitivity(new_sens)
        self.destroy()
