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
        # Simulate CLI arguments
        cli_args_list = [
            "--input_dir", "cli_input",
            "--output_dir", "cli_output",
            "--keep_split_card_images",
            "--crawl_directories",
            "--save_segmented_images",
            "--save_segmented_images_path", "cli_segmented_path",
        ]

        # Use CLIArgsParser to parse the arguments
        parser = CLIArgsParser()
        cli_args = parser.parse_args(cli_args_list)

        # Initialize ConfigManager with the parsed CLI args
        config_manager = ConfigManager(cli_args=cli_args)

        # Assert that the config values reflect the CLI overrides
        self.assertEqual(config_manager.get_input_path(), "cli_input")
        self.assertEqual(config_manager.get_output_path(), "cli_output")
        self.assertEqual(config_manager.get_keep_split_card_images(), True)
        self.assertEqual(config_manager.get_crawl_directories(), True)
        self.assertEqual(config_manager.get_save_segmented_images(), True)
        self.assertEqual(config_manager.get_save_segmented_images_path(), "cli_segmented_path")
