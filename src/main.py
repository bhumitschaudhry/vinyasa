from queue import Queue
from threading import Thread
from tkinter import Button, Tk
from tkinter.ttk import Label, Labelframe, Scale

import cv2
from PIL import Image, ImageTk

import model


class Vinyasa(Tk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.quitProcesses)
        self.flip = True
        self.run = True
        self.fps = 60
        self.delay = 1/self.fps

        self.imageQueue = Queue()
        self.pixels = 10

        self.trackThread = Thread(target=self.sendToTrack)

        self.geometry("500x500")
        for i in range(3):
            self.columnconfigure(i, weight=1)
            self.rowconfigure(i, weight=1)

        # Displaying video from a video source
        self.videoFrame = Labelframe(text="Video Device", labelanchor="nw")
        self.videoFrame.rowconfigure(0, weight=1)
        self.videoFrame.columnconfigure(0, weight=1)
        self.videoFrame.grid(row=0, column=0, rowspan=2,
                             columnspan=2, padx=10, pady=10, sticky="NSEW")

        self.videoDisplay = Label(self.videoFrame)
        self.videoDisplay.grid(row=0, column=0, sticky="NSEW")

        self.flipButton = Button(self, text="FLIP!", command=self.setFlip)
        self.flipButton.grid(row=2, column=0, columnspan=2,
                             padx=10, pady=10, sticky="NSEW")

        # Mouse Control
        self.controlFrame = Labelframe(
            self, text="Mouse Controls", labelanchor="ne")
        self.controlFrame.grid(row=0, column=2, rowspan=3,
                               padx=10, pady=10, sticky="NSEW")
        for i in range(6):
            self.controlFrame.rowconfigure(i, weight=1)
        self.controlFrame.columnconfigure(0, weight=1)

        Label(self.controlFrame, text="Mouse Sensitivity").grid(
            row=0, column=0, sticky="SEW")
        Scale(self.controlFrame, from_=1, to=100, orient='horizontal',
              value=1).grid(row=1, column=0, sticky="NEW")

        Label(self.controlFrame, text="Lines per Second").grid(
            row=2, column=0, sticky="SEW")
        Scale(self.controlFrame, from_=1, to=10, orient='horizontal',
              value=1).grid(row=3, column=0, sticky="NEW")

        Label(self.controlFrame, text="Cursor Size").grid(
            row=4, column=0, sticky="SEW")
        Scale(self.controlFrame, from_=1, to=5, orient='horizontal',
              value=1).grid(row=5, column=0, sticky="NEW")

        self.start()

    def start(self):
        self.camera = cv2.VideoCapture(0)
        self.runCamera(self.camera)
        self.trackThread.start()

    def quitProcesses(self):
        self.camera.release()
        self.trackThread.join()
        self.quit()
        exit()

    def setFlip(self):
        self.flip = False if self.flip else True

    def runCamera(self, camera):
        ret, self.frame = camera.read()
        if ret:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = cv2.flip(self.frame, 1) if self.flip else self.frame
            self.imageQueue.put_nowait(self.frame)

            self.image = Image.fromarray(self.frame)
            width = self.videoFrame.winfo_width()
            height = self.videoFrame.winfo_height()
            self.image.thumbnail((width, height), resample=Image.BICUBIC)
            self.image = ImageTk.PhotoImage(image=self.image)
            self.videoDisplay.config(image=self.image)
            self.after(int(self.delay*1000), self.runCamera, camera)

    def sendToTrack(self):
        while self.run:
            try:
                image = self.imageQueue.get(timeout=self.delay)
                model.trackFace(image, self.pixels)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    App = Vinyasa()
    App.mainloop()
