import tkinter as tk
import customtkinter as ctk

class CalibrationWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, mouse_controller):
        super().__init__(parent)
        self.title("Calibration Wizard")
        self.geometry("460x360")
        self.config = config
        self.mouse = mouse_controller
        
        # Make it modal-like
        self.attributes("-topmost", True)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Calibration Wizard", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        info_text = "Move your head to the extremes to test sensitivity. Adjust the slider below to your comfort."
        ctk.CTkLabel(main_frame, text=info_text, wraplength=380).pack(pady=(0, 20))
        
        # Directions sensitivity
        sens_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        sens_frame.pack(fill=tk.X, expand=True, padx=20)
        
        ctk.CTkLabel(sens_frame, text="Current Sensitivity:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sens_val_label = ctk.CTkLabel(sens_frame, text=f"{int(self.mouse.sensitivity)}")
        self.sens_val_label.grid(row=0, column=1, sticky=tk.W, padx=10)

        self.sens_scale = ctk.CTkSlider(sens_frame, from_=1, to=100, command=self.on_sens_change)
        self.sens_scale.set(self.mouse.sensitivity)
        self.sens_scale.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=20)
        
        sens_frame.columnconfigure(0, weight=1)
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(20, 20), padx=20)
        
        self.save_button = ctk.CTkButton(btn_frame, text="Save Calibration", command=self.save_and_close)
        self.save_button.pack(side=tk.RIGHT)
        
        self.cancel_button = ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=2, command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=10)

    def on_sens_change(self, value):
        self.sens_val_label.configure(text=f"{int(value)}")
        
    def save_and_close(self):
        new_sens = int(self.sens_scale.get())
        self.mouse.set_sensitivity(new_sens)
        self.destroy()
