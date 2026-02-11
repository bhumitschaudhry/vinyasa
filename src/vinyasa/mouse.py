"""
Mouse control module using PyAutoGUI.
Translates model predictions into system-level mouse movements and clicks.
"""

import pyautogui
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)

class MouseController:
    """
    Interfaces with the OS to simulate mouse movements and clicks.
    Includes acceleration logic for smoother user experience.
    """
    def __init__(self, sensitivity: int = 10, pause: float = 0, failsafe: bool = True):
        """
        Initialize the controller.
        
        Args:
            sensitivity: Base number of pixels to move per step.
            pause: Delay after each PyAutoGUI call.
            failsafe: If True, moving mouse to a corner aborts the script.
        """
        self.sensitivity = sensitivity
        self.acceleration = 1.0
        self.last_direction: Optional[str] = None
        self.direction_count = 0
        
        pyautogui.PAUSE = pause
        pyautogui.FAILSAFE = failsafe
        
    def set_sensitivity(self, value: float):
        """Updates the movement sensitivity."""
        self.sensitivity = int(float(value))
        
    def move(self, direction: str):
        """
        Simulates mouse movement in the specified direction.
        Applies acceleration if the direction is consistent.
        """
        if direction == self.last_direction:
            self.direction_count += 1
            if self.direction_count > 5:
                # Increase speed up to 3x base sensitivity
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
                error_msg += " On macOS, ensure 'Accessibility' permissions are granted."
            elif sys.platform == "linux":
                error_msg += " On Linux, ensure you are using X11 (Wayland is not supported)."
            logger.error(error_msg)
            
    def click(self, button: str = "left"):
        """Simulates a mouse click."""
        try:
            pyautogui.click(button=button)
        except pyautogui.FailSafeException:
            logger.error("PyAutoGUI FailSafe triggered during click.")
            
    def execute_command(self, label: str):
        """
        Main entry point for executing commands based on model labels.
        
        Args:
            label: The class name predicted by the model (e.g., 'Left', 'Left Click').
        """
        if label in ["Left", "Right", "Up", "Down", "Center"]:
            self.move(label)
        elif label == "Left Click":
            self.click("left")
        elif label == "Right Click":
            self.click("right")
