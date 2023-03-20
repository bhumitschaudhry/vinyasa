import cv2
from PIL import Image, ImageTk

import model

from queue import Queue
from tkinter import Tk, Button
from tkinter.ttk import Scale, Label, Labelframe

class Vinyasa(Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.quitProcesses)
        self.flip = True
        self.run = True

        self.imageQueue = Queue()
        self.pixels = 10

        self.geometry("500x500")
        for i in range(3):
            self.columnconfigure(i, weight=1)
            self.rowconfigure(i, weight=1)
        
        # Displaying video from a video source
        self.videoFrame = Labelframe(text="Video Device", labelanchor="nw")
        self.videoFrame.rowconfigure(0, weight=1)
        self.videoFrame.columnconfigure(0, weight=1)
        self.videoFrame.grid(row=0, column=0, rowspan=2, columnspan=2, padx=10, pady=10, sticky="NSEW")

        self.videoDisplay = Label(self.videoFrame)
        self.videoDisplay.grid(row=0, column=0, sticky="NSEW")

        self.flipButton = Button(self, text="FLIP!", command=self.setFlip)
        self.flipButton.grid(row=2, column=0, columnspan=2,  padx=10, pady=10, sticky="NSEW")

        # Mouse Control
        self.controlFrame = Labelframe(self, text="Mouse Controls", labelanchor="ne")
        self.controlFrame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="NSEW")
        for i in range(6):
            self.controlFrame.rowconfigure(i, weight=1)
        self.controlFrame.columnconfigure(0, weight=1)
        

        Label(self.controlFrame, text="Mouse Sensitivity").grid(row=0, column=0, sticky="SEW")
        Scale(self.controlFrame, from_=1, to=100, orient='horizontal', value=1).grid(row=1, column=0, sticky="NEW")

        Label(self.controlFrame, text="Lines per Second").grid(row=2, column=0, sticky="SEW")
        Scale(self.controlFrame, from_=1, to=10, orient='horizontal', value=1).grid(row=3, column=0, sticky="NEW")

        Label(self.controlFrame, text="Cursor Size").grid(row=4, column=0, sticky="SEW")
        Scale(self.controlFrame, from_=1, to=5, orient='horizontal', value=1).grid(row=5, column=0, sticky="NEW")

        self.camera = cv2.VideoCapture(0)

        self.start()


    def start(self):
        self.startCamera(self.camera)
        self.sendToTrack()

    def quitProcesses(self):
        self.camera.release()
        self.quit()
        exit()

    def setFlip(self):
        self.flip = False if self.flip else True


    def startCamera(self, camera):
        ret, self.frame = camera.read()
        if ret:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = cv2.flip(self.frame, 1) if self.flip else self.frame
            self.imageQueue.put(self.frame)

            self.image = Image.fromarray(self.frame)
            self.image.thumbnail((self.videoFrame.winfo_height(), self.videoFrame.winfo_width()), resample=Image.BICUBIC)
            self.image = ImageTk.PhotoImage(image=self.image)
            self.videoDisplay.config(image=self.image)
            
            self.after(16, self.startCamera, camera)
    
    def sendToTrack(self):
        try:
            image = self.imageQueue.get_nowait()
            model.trackFace(image, self.pixels)
            self.after(500, self.sendToTrack)
        except:
            pass


if __name__ == "__main__":
    App = Vinyasa()
    App.mainloop()


