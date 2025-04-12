import unittest
from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def test_config_values(self):
        config_manager = ConfigManager()
        self.assertEqual(config_manager.get_input_path(), "data/input")
        self.assertEqual(config_manager.get_output_path(), "data/output")
        self.assertEqual(config_manager.get_threshold(), 0.5)
        self.assertEqual(config_manager.get_api_key(), "your_api_key_here")

if __name__ == "__main__":
    unittest.main()
