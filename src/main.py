import tkinter as tk
from vinyasa.app import VinyasaApp
import sys
import os

# Add the current directory to sys.path so we can import the vinyasa package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    root = tk.Tk()
    # Use a themed style if available
    try:
        from ttkthemes import ThemedStyle
        style = ThemedStyle(root)
        style.set_theme("arc")
    except ImportError:
        pass
        
    app = VinyasaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
