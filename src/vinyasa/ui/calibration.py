"""
Calibration Wizard Module.
Provides a modal window for users to standardize their head tracking sensitivity.
"""

import tkinter as tk
import customtkinter as ctk

class CalibrationWindow(ctk.CTkToplevel):
    """
    A modal-like window for fine-tuning mouse sensitivity.
    """
    def __init__(self, parent, config, mouse_controller):
        """
        Initialize the calibration window.
        
        Args:
            parent: The parent window.
            config: Application configuration instance.
            mouse_controller: Mouse controller instance to update.
        """
        super().__init__(parent)
        self.title("Calibration Wizard")
        self.geometry("500x400")
        self.config = config
        self.mouse = mouse_controller
        
        # UI Policy: Stay on top and grab focus
        self.attributes("-topmost", True)
        self.grab_set()
        
        # Design Specs: Light Theme
        self.configure(fg_color="#F0F0F0")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Builds the calibration UI."""
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        ctk.CTkLabel(main_frame, text="CALIBRATION", 
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="black").pack(pady=(30, 15))
        
        info_text = "Standardize your head movements. Adjust the base sensitivity to your comfort level for the best tracking experience."
        ctk.CTkLabel(main_frame, text=info_text, wraplength=380, text_color="#666666").pack(pady=(0, 30))
        
        # Feedback Section
        sens_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        sens_frame.pack(fill=tk.X, padx=40)
        
        ctk.CTkLabel(sens_frame, text="Sensitivity Index:", font=ctk.CTkFont(weight="bold"), text_color="black").pack(side=tk.LEFT)
        self.sens_val_label = ctk.CTkLabel(sens_frame, text=f"{int(self.mouse.sensitivity)}",
                                           font=ctk.CTkFont(family="Courier", size=16, weight="bold"),
                                           text_color="#3B8ED0")
        self.sens_val_label.pack(side=tk.LEFT, padx=15)

        # Main Slider
        self.sens_scale = ctk.CTkSlider(main_frame, from_=1, to=100, number_of_steps=99,
                                        command=self.on_sens_change,
                                        button_color="#3B8ED0", progress_color="#3B8ED0")
        self.sens_scale.set(self.mouse.sensitivity)
        self.sens_scale.pack(fill=tk.X, pady=(20, 10), padx=40)
        
        # Controls
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 30), padx=40)
        
        self.save_button = ctk.CTkButton(btn_frame, text="APPLY", 
                                         height=35, corner_radius=10,
                                         fg_color="#3B8ED0", hover_color="#367E96",
                                         command=self.save_and_close)
        self.save_button.pack(side=tk.RIGHT)
        
        self.cancel_button = ctk.CTkButton(btn_frame, text="CANCEL", 
                                          height=35, corner_radius=10,
                                          fg_color="transparent", border_width=2, 
                                          text_color="black",
                                          command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=15)

    def on_sens_change(self, value):
        """Callback for slider movement."""
        self.sens_val_label.configure(text=f"{int(value)}")
        
    def save_and_close(self):
        """Saves settings and closes the window."""
        new_sens = int(self.sens_scale.get())
        self.mouse.set_sensitivity(new_sens)
        self.destroy()
