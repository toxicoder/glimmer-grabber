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
        # Create CLI arguments to override the defaults
        parser = argparse.ArgumentParser()
        parser.add_argument("input_dir", nargs='?', default=None)
        parser.add_argument("output_dir", nargs='?', default=None)
        parser.add_argument("--keep_split_card_images", action="store_true")
        parser.add_argument("--crawl_directories", action="store_true")
        parser.add_argument("--save_segmented_images", action="store_true")
        parser.add_argument("--save_segmented_images_path")
        cli_args = parser.parse_args([
            "cli_input",
            "cli_output",
            "--keep_split_card_images",
            "--save_segmented_images",
            "--save_segmented_images_path", "cli_segmented_path",
        ])

        # Initialize ConfigManager with the CLI args
        config_manager = ConfigManager(cli_args=cli_args)

        # Assert that the config values reflect the CLI overrides
        self.assertEqual(config_manager.get_input_path(), "cli_input")
        self.assertEqual(config_manager.get_output_path(), "cli_output")
        self.assertEqual(config_manager.get_keep_split_card_images(), True)
        self.assertEqual(config_manager.get_crawl_directories(), True)  # Default value
        self.assertEqual(config_manager.get_save_segmented_images(), True)
        self.assertEqual(config_manager.get_save_segmented_images_path(), "cli_segmented_path")
