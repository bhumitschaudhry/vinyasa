import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock tensorflow to avoid import errors in environment without it
sys.modules['tensorflow'] = MagicMock()

from vinyasa.mouse import MouseController

class TestMouseController(unittest.TestCase):
    def setUp(self):
        self.mouse = MouseController(sensitivity=10, pause=0, failsafe=False)

    @patch('pyautogui.move')
    def test_move_left(self, mock_move):
        self.mouse.move("Left")
        mock_move.assert_called_with(-10, 0)

    @patch('pyautogui.move')
    def test_move_right(self, mock_move):
        self.mouse.move("Right")
        mock_move.assert_called_with(10, 0)

    @patch('pyautogui.click')
    def test_click(self, mock_click):
        self.mouse.click("left")
        mock_click.assert_called_with(button="left")

    def test_acceleration(self):
        with patch('pyautogui.move') as mock_move:
            # Move same direction multiple times
            for _ in range(10):
                self.mouse.move("Left")
            
            # Acceleration should increase
            self.assertGreater(self.mouse.acceleration, 1.0)
            
            # Move different direction
            self.mouse.move("Right")
            self.assertEqual(self.mouse.acceleration, 1.0)

if __name__ == '__main__':
    unittest.main()
