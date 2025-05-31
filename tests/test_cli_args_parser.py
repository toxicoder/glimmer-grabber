import unittest
import argparse
from src.app.cli_args_parser import CLIArgsParser, AppConfig

class TestCLIArgsParser(unittest.TestCase):
    """Tests for the CLIArgsParser class."""

    def setUp(self):
        """Set up test environment."""
        self.parser = CLIArgsParser()

    def test_required_arguments(self):
        """Test that required arguments are correctly parsed."""
        with self.assertRaises(SystemExit): # Argparse exits on error
            self.parser.parser.parse_args([]) # No arguments

        with self.assertRaises(SystemExit):
            self.parser.parser.parse_args(["input_dir_val"]) # Missing output_dir

        # Test with both required arguments
        # parse_arguments() calls parser.parse_args() and then map_arguments_to_config()
        # For direct Namespace output, we call self.parser.parser.parse_args()
        args_namespace = self.parser.parser.parse_args(["input_val", "output_val"])
        self.assertEqual(args_namespace.input_dir, "input_val")
        self.assertEqual(args_namespace.output_dir, "output_val")

    def test_optional_arguments_present(self):
        """Test that optional arguments are correctly parsed when present."""
        args_namespace = self.parser.parser.parse_args([
            "input_val", "output_val",
            "--keep_split_card_images",
            "--save_segmented_images",
            "--save_segmented_images_path", "segmented_path_val",
            "--history_file_path", "history_path_val",
            "--config_file", "custom_config.json",
            "--yolo_model_path", "custom_model.pt",
            "--api_url", "http://customapi.com",
            "--cache_duration", "7200",
            "--segmentation_confidence_threshold", "0.65"
        ])
        self.assertTrue(args_namespace.keep_split_card_images)
        self.assertTrue(args_namespace.save_segmented_images)
        self.assertEqual(args_namespace.save_segmented_images_path, "segmented_path_val")
        self.assertEqual(args_namespace.history_file_path, "history_path_val")
        self.assertEqual(args_namespace.config_file, "custom_config.json")
        self.assertEqual(args_namespace.yolo_model_path, "custom_model.pt")
        self.assertEqual(args_namespace.api_url, "http://customapi.com")
        self.assertEqual(args_namespace.cache_duration, 7200) # argparse converts to int
        self.assertEqual(args_namespace.segmentation_confidence_threshold, 0.65) # argparse converts to float


    def test_optional_arguments_defaults(self):
        """Test default values for optional arguments when not present."""
        args_namespace = self.parser.parser.parse_args(["input_val", "output_val"])

        # Flags default to False if not 'store_true' with default=True
        self.assertFalse(args_namespace.keep_split_card_images)
        self.assertFalse(args_namespace.save_segmented_images)
        # crawl_directories has default=True in CLIArgsParser
        self.assertTrue(args_namespace.crawl_directories)

        # Valued arguments default to None if not specified
        self.assertIsNone(args_namespace.save_segmented_images_path)
        self.assertIsNone(args_namespace.history_file_path)
        self.assertIsNone(args_namespace.config_file)
        self.assertIsNone(args_namespace.yolo_model_path)
        self.assertIsNone(args_namespace.api_url)
        self.assertIsNone(args_namespace.cache_duration)
        self.assertIsNone(args_namespace.segmentation_confidence_threshold)

    def test_map_arguments_to_config(self):
        """Test the mapping of parsed argparse.Namespace to AppConfig dictionary."""
        args_namespace = self.parser.parser.parse_args([
            "input_mapped", "output_mapped",
            "--api_url", "http://mappedapi.com",
            "--yolo_model_path", "mapped_model.pt",
            # Leave some args out to ensure they are not in the mapped config if None
        ])

        # The parse_arguments method in CLIArgsParser does the mapping.
        # However, ConfigManager now takes the Namespace directly.
        # If we want to test map_arguments_to_config in isolation:
        app_config: AppConfig = self.parser.map_arguments_to_config(args_namespace)

        self.assertEqual(app_config.get("input_path"), "input_mapped")
        self.assertEqual(app_config.get("output_path"), "output_mapped")
        self.assertEqual(app_config.get("api_url"), "http://mappedapi.com")
        self.assertEqual(app_config.get("yolo_model_path"), "mapped_model.pt")

        # crawl_directories is True by default in argparse, so it should be in mapped config
        self.assertTrue(app_config.get("crawl_directories"))

        # Arguments not provided (and thus None in Namespace, or False for store_true flags)
        # should not appear in the config dict from map_arguments_to_config
        # because of `if value is not None:` check.
        # However, boolean flags that are False ARE included by map_arguments_to_config
        # if their default in argparse is False and they are not specified.
        # This needs to be consistent with ConfigManager's update_with_cli_args.
        # map_arguments_to_config will only include if hasattr and getattr is not None.
        # So, False booleans (from store_true not being present) are NOT in the dict.
        self.assertNotIn("keep_split_card_images", app_config) # default is False, not in dict
        self.assertNotIn("cache_duration", app_config) # default is None, not in dict

    def test_parse_arguments_method(self):
        """Test the main parse_arguments() method of CLIArgsParser."""
        # This method returns the Namespace, not the mapped dict.
        # The mapped dict is an internal detail used by ConfigManager if it were to call it.
        # ConfigManager.update_with_cli_args works directly with the Namespace.

        # To test this, we need to patch sys.argv or pass args to parse_args()
        test_cli_args = [
            "input_main", "output_main",
            "--segmentation_confidence_threshold", "0.9"
        ]

        # Patch sys.argv for the duration of this test
        with patch('sys.argv', ['script_name'] + test_cli_args):
            parsed_namespace = self.parser.parse_arguments()

        self.assertEqual(parsed_namespace.input_dir, "input_main")
        self.assertEqual(parsed_namespace.output_dir, "output_main")
        self.assertEqual(parsed_namespace.segmentation_confidence_threshold, 0.9)
        self.assertTrue(parsed_namespace.crawl_directories) # Default
        self.assertIsNone(parsed_namespace.api_url) # Not provided

if __name__ == "__main__":
    unittest.main()
