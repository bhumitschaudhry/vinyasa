import cv2
import numpy as np
from PIL import Image, ImageTk

from tkinter import Tk, Label

import threading
# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

class Vinyasa(Tk):
    def __init__(self):
        super().__init__()
        self.image = None

        self.geometry("500x500")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.videoDisplay = Label(self)
        self.videoDisplay.grid(row=0, column=0, sticky="NSEW")

        self.camera = cv2.VideoCapture(0)
        self.startCamera()
    def startCamera(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            self.image = Image.fromarray(frame)
            self.image.thumbnail((self.videoDisplay.winfo_height(), self.videoDisplay.winfo_width()), resample=Image.BICUBIC)
            self.image = ImageTk.PhotoImage(image=self.image)
            self.videoDisplay.config(image=self.image)
            self.after(16, self.startCamera)


App = Vinyasa()
App.mainloop()


