import tkinter as tk
import customtkinter as ctk

class CalibrationWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, mouse_controller):
        super().__init__(parent)
        self.title("Calibration Wizard")
        self.geometry("500x400")
        self.config = config
        self.mouse = mouse_controller
        
        # Make it modal-like
        self.attributes("-topmost", True)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self, corner_radius=15, border_width=1, border_color="#333333")
        main_frame.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")

        ctk.CTkLabel(main_frame, text="CALIBRATION WIZARD", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 15))
        
        info_text = "Standardize your head tracking movement. Move your head to the extremes to test sensitivity, then adjust the slider to match your comfort level."
        ctk.CTkLabel(main_frame, text=info_text, wraplength=380, text_color="gray").pack(pady=(0, 30))
        
        # Directions sensitivity
        sens_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        sens_frame.pack(fill=tk.X, padx=40)
        
        header_sens = ctk.CTkFrame(sens_frame, fg_color="transparent")
        header_sens.pack(fill=tk.X)
        
        ctk.CTkLabel(header_sens, text="Sensitivity Index:", 
                     font=ctk.CTkFont(weight="bold")).pack(side=tk.LEFT)
        self.sens_val_label = ctk.CTkLabel(header_sens, text=f"{int(self.mouse.sensitivity)}",
                                           font=ctk.CTkFont(family="Courier", size=16, weight="bold"),
                                           text_color=["#3B8ED0", "#1F6AA5"])
        self.sens_val_label.pack(side=tk.LEFT, padx=15)

        self.sens_scale = ctk.CTkSlider(sens_frame, from_=1, to=100, number_of_steps=99,
                                        command=self.on_sens_change)
        self.sens_scale.set(self.mouse.sensitivity)
        self.sens_scale.pack(fill=tk.X, pady=(20, 10))
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 30), padx=40)
        
        self.save_button = ctk.CTkButton(btn_frame, text="APPLY & SAVE", 
                                         height=35, corner_radius=8,
                                         command=self.save_and_close)
        self.save_button.pack(side=tk.RIGHT)
        
        self.cancel_button = ctk.CTkButton(btn_frame, text="CANCEL", 
                                          height=35, corner_radius=8,
                                          fg_color="transparent", border_width=2, 
                                          command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=15)

    def on_sens_change(self, value):
        self.sens_val_label.configure(text=f"{int(value)}")
        
    def save_and_close(self):
        new_sens = int(self.sens_scale.get())
        self.mouse.set_sensitivity(new_sens)
        self.destroy()
