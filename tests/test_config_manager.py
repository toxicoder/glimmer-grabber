import unittest
import argparse
import tempfile
import os
import json
from src.app.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Tests for the ConfigManager class."""
    def test_config_values(self) -> None:
        """Test retrieval of configuration values.

        This test verifies that the ConfigManager correctly retrieves configuration
        values from the config.json file. It checks the values for input path,
        output path, threshold, and API key.
        """
        config_manager: ConfigManager = ConfigManager()
        self.assertEqual(config_manager.get_input_path(), None)
        self.assertEqual(config_manager.get_output_path(), None)
        self.assertEqual(config_manager.get_threshold(), None)
        self.assertEqual(config_manager.get_api_key(), None)
        self.assertEqual(config_manager.get_keep_split_card_images(), None)
        self.assertEqual(config_manager.get_crawl_directories(), None)
        self.assertEqual(config_manager.get_save_segmented_images(), None)
        self.assertEqual(config_manager.get_save_segmented_images_path(), None)

    def test_cli_arg_overrides(self) -> None:
        """Test that CLI arguments override config file settings."""
        # Create a dictionary to simulate CLI arguments
        cli_args = {
            "input_dir": "cli_input",
            "output_dir": "cli_output",
            "keep_split_card_images": True,
            "crawl_directories": False,  # Explicitly set to False
            "save_segmented_images": True,
            "save_segmented_images_path": "cli_segmented_path",
        }

        # Initialize ConfigManager with the simulated CLI args
        config_manager = ConfigManager(cli_args=argparse.Namespace(**cli_args))

        # Assert that the config values reflect the CLI overrides
        self.assertEqual(config_manager.get_input_path(), "cli_input")
        self.assertEqual(config_manager.get_output_path(), "cli_output")
        self.assertEqual(config_manager.get_keep_split_card_images(), True)
        self.assertEqual(config_manager.get_crawl_directories(), False)
        self.assertEqual(config_manager.get_save_segmented_images(), True)
        self.assertEqual(config_manager.get_save_segmented_images_path(), "cli_segmented_path")
