import unittest
from typing import Optional
from glimmer_grabber.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Tests for the ConfigManager class."""
    def test_config_values(self) -> None:
        """Test retrieval of configuration values.

        This test verifies that the ConfigManager correctly retrieves configuration
        values from the config.json file. It checks the values for input path,
        output path, threshold, and API key.
        """
        config_manager: ConfigManager = ConfigManager()
        self.assertEqual(config_manager.get_input_path(), "data/input")
        self.assertEqual(config_manager.get_output_path(), "data/output")
        self.assertEqual(config_manager.get_threshold(), 0.5)
        self.assertEqual(config_manager.get_api_key(), "your_api_key_here")

if __name__ == "__main__":
    unittest.main()
