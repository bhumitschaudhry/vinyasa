import customtkinter as ctk
from vinyasa.app import VinyasaApp
import sys
import os

# Add the current directory to sys.path so we can import the vinyasa package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    app_root = ctk.CTk()
    app = VinyasaApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app_root.mainloop()

if __name__ == "__main__":
    main()
