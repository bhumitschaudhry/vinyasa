import unittest
import os
import json
import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['tensorflow'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['darkdetect'] = MagicMock()

from vinyasa.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config_file = "test_config.json"
        Config.CONFIG_FILE = self.config_file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        Config.CONFIG_FILE = "config.json"

    def test_save_load(self):
        config = Config()
        config.INITIAL_SENSITIVITY = 25
        config.save()
        
        new_config = Config.load()
        self.assertEqual(new_config.INITIAL_SENSITIVITY, 25)

if __name__ == '__main__':
    unittest.main()
