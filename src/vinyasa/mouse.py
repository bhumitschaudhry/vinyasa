import pyautogui
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)

class MouseController:
    def __init__(self, sensitivity: int = 10, pause: float = 0, failsafe: bool = True):
        self.sensitivity = sensitivity
        self.acceleration = 1.0
        self.last_direction: Optional[str] = None
        self.direction_count = 0
        pyautogui.PAUSE = pause
        pyautogui.FAILSAFE = failsafe
        
    def set_sensitivity(self, value: float):
        self.sensitivity = int(float(value))
        
    def move(self, direction: str):
        if direction == self.last_direction:
            self.direction_count += 1
            if self.direction_count > 5:
                self.acceleration = min(3.0, self.acceleration + 0.1)
        else:
            self.last_direction = direction
            self.direction_count = 0
            self.acceleration = 1.0

        move_amount = int(self.sensitivity * self.acceleration)
        
        try:
            match direction:
                case "Left":
                    pyautogui.move(-move_amount, 0)
                case "Right":
                    pyautogui.move(move_amount, 0)
                case "Up":
                    pyautogui.move(0, -move_amount)
                case "Down":
                    pyautogui.move(0, move_amount)
                case "Center":
                    self.acceleration = 1.0
                    self.direction_count = 0
        except pyautogui.FailSafeException:
            error_msg = "PyAutoGUI FailSafe triggered."
            if sys.platform == "darwin":
                error_msg += " On macOS, ensure 'Accessibility' permissions are granted to the terminal/IDE."
            elif sys.platform == "linux":
                error_msg += " On Linux, this may fail on Wayland; try switching to X11."
            logger.error(error_msg)
            
    def click(self, button: str = "left"):
        try:
            pyautogui.click(button=button)
        except pyautogui.FailSafeException:
            logger.warning("PyAutoGUI FailSafe triggered during click.")
            
    def execute_command(self, label: str):
        if label in ["Left", "Right", "Up", "Down", "Center"]:
            self.move(label)
        elif label == "Left Click":
            self.click("left")
        elif label == "Right Click":
            self.click("right")
