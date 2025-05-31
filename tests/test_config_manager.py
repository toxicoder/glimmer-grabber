import unittest
import argparse
import tempfile
import os
import json
from src.app.config_manager import ConfigManager, AppConfig # Import AppConfig for type hinting
from src.app.cli_args_parser import CLIArgsParser # Needed to simulate parsed CLI args

class TestConfigManager(unittest.TestCase):
    """Tests for the ConfigManager class."""

    def setUp(self):
        """Set up for test methods."""
        # Create a temporary directory to hold dummy config files
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup) # Ensure cleanup even if tests fail

        # Default values from ConfigManager for comparison
        self.cm_defaults = {
            "api_url": ConfigManager.DEFAULT_API_URL,
            "cache_file_name": ConfigManager.DEFAULT_CACHE_FILE_NAME,
            "cache_duration": ConfigManager.DEFAULT_CACHE_DURATION,
            "yolo_model_path": ConfigManager.DEFAULT_YOLO_MODEL_PATH,
            "log_file_name": ConfigManager.DEFAULT_LOG_FILE_NAME,
            "history_file_name": ConfigManager.DEFAULT_HISTORY_FILE_NAME, # For constructing default history_file_path
            "segmentation_confidence_threshold": ConfigManager.DEFAULT_SEGMENTATION_CONFIDENCE_THRESHOLD,
            "image_preprocessing_settings": ConfigManager.DEFAULT_IMAGE_PREPROCESSING_SETTINGS,
            "keep_split_card_images": False, # Default from get_ method
            "crawl_directories": True,     # Default from get_ method
            "save_segmented_images": False,# Default from get_ method
            # input_path, output_path, save_segmented_images_path, api_key, threshold are None by default
            "input_path": None,
            "output_path": None,
            "save_segmented_images_path": None,
            "api_key": None,
            "threshold": None,
        }
        self.default_history_base_path = os.path.join("data", self.cm_defaults["history_file_name"])


    def _create_dummy_config_file(self, data: Dict[str, Any]) -> str:
        """Helper to create a temporary JSON config file."""
        # Use a fixed name for the dummy config file within the temp directory
        config_file_path = os.path.join(self.test_dir.name, "temp_config.json")
        with open(config_file_path, "w") as f:
            json.dump(data, f)
        return config_file_path

    def test_01_default_values_no_file_no_cli(self):
        """Test that ConfigManager loads its internal defaults when no config file or CLI args are provided."""
        # Initialize ConfigManager with a non-existent config file path and no CLI args
        # This forces it to rely on its internal defaults for everything not set by CLI (which is nothing here)
        cm = ConfigManager(config_file=os.path.join(self.test_dir.name, "non_existent_config.json"), cli_args=None)

        self.assertEqual(cm.get_api_url(), self.cm_defaults["api_url"])
        self.assertEqual(cm.get_cache_file_name(), self.cm_defaults["cache_file_name"])
        self.assertEqual(cm.get_cache_duration(), self.cm_defaults["cache_duration"])
        self.assertEqual(cm.get_yolo_model_path(), self.cm_defaults["yolo_model_path"])
        self.assertEqual(cm.get_log_file_name(), self.cm_defaults["log_file_name"])
        # history_file_path depends on output_path, which is None here, so it defaults to data/
        self.assertEqual(cm.get_history_file_path(), self.default_history_base_path)
        self.assertEqual(cm.get_segmentation_confidence_threshold(), self.cm_defaults["segmentation_confidence_threshold"])
        self.assertEqual(cm.get_image_preprocessing_settings(), self.cm_defaults["image_preprocessing_settings"])

        self.assertEqual(cm.get_input_path(), self.cm_defaults["input_path"]) # None
        self.assertEqual(cm.get_output_path(), self.cm_defaults["output_path"]) # None
        self.assertEqual(cm.get_api_key(), self.cm_defaults["api_key"]) # None
        self.assertEqual(cm.get_threshold(), self.cm_defaults["threshold"]) # None

        self.assertEqual(cm.get_keep_split_card_images(), self.cm_defaults["keep_split_card_images"]) # False
        self.assertEqual(cm.get_crawl_directories(), self.cm_defaults["crawl_directories"]) # True
        self.assertEqual(cm.get_save_segmented_images(), self.cm_defaults["save_segmented_images"]) # False
        self.assertEqual(cm.get_save_segmented_images_path(), self.cm_defaults["save_segmented_images_path"]) # None

    def test_02_load_from_json_file(self):
        """Test loading configuration from a JSON file."""
        json_data = {
            "input_path": "json_input/",
            "output_path": "json_output/",
            "api_url": "http://json-api.com",
            "cache_duration": 7200,
            "yolo_model_path": "json_model.pt",
            "log_file_name": "json_app.log",
            "segmentation_confidence_threshold": 0.75,
            "image_preprocessing_settings": {
                "contrast_check_threshold": 0.40,
                "ocr_preprocessing": {"clahe_clip_limit": 3.0}
            },
            "crawl_directories": False # Override default True
        }
        config_file_path = self._create_dummy_config_file(json_data)
        cm = ConfigManager(config_file=config_file_path, cli_args=None)

        self.assertEqual(cm.get_input_path(), "json_input/")
        self.assertEqual(cm.get_output_path(), "json_output/")
        self.assertEqual(cm.get_api_url(), "http://json-api.com")
        self.assertEqual(cm.get_cache_duration(), 7200)
        self.assertEqual(cm.get_yolo_model_path(), "json_model.pt")
        self.assertEqual(cm.get_log_file_name(), "json_app.log")
        self.assertEqual(cm.get_segmentation_confidence_threshold(), 0.75)

        # Test history_file_path construction with output_path from JSON
        expected_history_path = os.path.join("json_output/", "data", self.cm_defaults["history_file_name"])
        self.assertEqual(cm.get_history_file_path(), expected_history_path)

        # Test nested dict for image_preprocessing_settings
        retrieved_ips = cm.get_image_preprocessing_settings()
        self.assertEqual(retrieved_ips["contrast_check_threshold"], 0.40)
        # Check if default ocr_preprocessing settings are merged or replaced
        # Current ConfigManager replaces the whole dict, so other ocr defaults are gone.
        self.assertEqual(retrieved_ips["ocr_preprocessing"]["clahe_clip_limit"], 3.0)
        self.assertNotIn("clahe_tile_grid_size", retrieved_ips["ocr_preprocessing"]) # It was not in json_data

        self.assertEqual(cm.get_crawl_directories(), False) # Overridden
        self.assertEqual(cm.get_keep_split_card_images(), self.cm_defaults["keep_split_card_images"]) # Default (False)

    def test_03_cli_overrides_defaults(self):
        """Test that CLI arguments override internal defaults when no config file is present."""
        # Simulate parsed CLI arguments (as if they came from CLIArgsParser.parse_arguments())
        cli_args = argparse.Namespace(
            input_dir="cli_input_only/", # input_dir from CLIArgsParser maps to input_path
            output_dir="cli_output_only/",# output_dir from CLIArgsParser maps to output_path
            api_url="http://cli-api.com",
            cache_duration=1800,
            yolo_model_path="cli_model.pt",
            log_file_name="cli_app.log", # This is not a CLI arg, so it won't be overridden by this
            segmentation_confidence_threshold=0.8,
            keep_split_card_images=True, # A flag, will be True
            # For args not in CLIArgsParser's list, they won't be in cli_args Namespace
            # e.g. crawl_directories will be its argparse default (True) if not passed.
            # Let's assume crawl_directories is NOT passed via CLI for this test, so it should be ConfigManager default
            crawl_directories=None, # Simulate not being passed or being None from parser
            save_segmented_images=None,
            save_segmented_images_path=None,
            history_file_path=None,
            config_file=None # important for ConfigManager init
        )

        cm = ConfigManager(config_file=os.path.join(self.test_dir.name, "non_existent_config.json"), cli_args=cli_args)

        self.assertEqual(cm.get_input_path(), "cli_input_only/")
        self.assertEqual(cm.get_output_path(), "cli_output_only/")
        self.assertEqual(cm.get_api_url(), "http://cli-api.com")
        self.assertEqual(cm.get_cache_duration(), 1800)
        self.assertEqual(cm.get_yolo_model_path(), "cli_model.pt")
        self.assertEqual(cm.get_segmentation_confidence_threshold(), 0.8)
        self.assertEqual(cm.get_keep_split_card_images(), True)

        # Values not overridden by CLI should take ConfigManager's defaults
        self.assertEqual(cm.get_log_file_name(), self.cm_defaults["log_file_name"]) # Was not a CLI arg in Namespace
        self.assertEqual(cm.get_crawl_directories(), self.cm_defaults["crawl_directories"]) # Was None in Namespace
        # history_file_path with output_path from CLI
        expected_history_path = os.path.join("cli_output_only/", "data", self.cm_defaults["history_file_name"])
        self.assertEqual(cm.get_history_file_path(), expected_history_path)

    def test_04_cli_overrides_json(self):
        """Test precedence: CLI arguments override JSON file settings."""
        json_data = {
            "output_path": "json_output_prec/", # Will be overridden by CLI
            "api_url": "http://json-api-prec.com", # Will be overridden by CLI
            "cache_duration": 7200, # JSON value
            "yolo_model_path": "json_model_prec.pt", # JSON value
            "log_file_name": "json_app_prec.log", # JSON value, no CLI override for this
        }
        config_file_path = self._create_dummy_config_file(json_data)

        # CLI args. Only output_dir and api_url are different from JSON.
        cli_args = argparse.Namespace(
            input_dir=None, # Not in JSON, not in CLI for this test of override
            output_dir="cli_output_prec/", # Overrides JSON's output_path
            api_url="http://cli-api-prec.com", # Overrides JSON
            cache_duration=None, # CLI does not provide, JSON value should be used
            yolo_model_path=None,  # CLI does not provide, JSON value should be used
            config_file=None # To prevent ConfigManager from trying to load another based on this
        )
        cm = ConfigManager(config_file=config_file_path, cli_args=cli_args)

        self.assertEqual(cm.get_output_path(), "cli_output_prec/") # CLI override
        self.assertEqual(cm.get_api_url(), "http://cli-api-prec.com") # CLI override

        self.assertEqual(cm.get_cache_duration(), 7200) # From JSON (CLI was None)
        self.assertEqual(cm.get_yolo_model_path(), "json_model_prec.pt") # From JSON (CLI was None)
        self.assertEqual(cm.get_log_file_name(), "json_app_prec.log") # From JSON (no CLI arg for this)

        # input_path was not in JSON or CLI, should be default None
        self.assertEqual(cm.get_input_path(), self.cm_defaults["input_path"])


    def test_05_all_getters_with_mixed_config(self):
        """Test all getter methods with a mix of defaults, JSON, and CLI."""
        json_data = {
            "api_url": "http://json-api.com",
            "cache_duration": 1000,
            "image_preprocessing_settings": {
                "contrast_check_threshold": 0.50,
                "ocr_preprocessing": {"clahe_clip_limit": 2.5}
            }
        }
        config_file_path = self._create_dummy_config_file(json_data)

        cli_args = argparse.Namespace(
            output_dir="cli_output_final/",
            api_url="http://cli-api.com", # Override JSON
            yolo_model_path="cli_yolo.pt", # CLI only
            keep_split_card_images=True,   # CLI only, override default False
            config_file=None
        )
        cm = ConfigManager(config_file=config_file_path, cli_args=cli_args)

        # --- Check values based on precedence: CLI > JSON > Default ---
        # output_path: CLI
        self.assertEqual(cm.get_output_path(), "cli_output_final/")
        # api_url: CLI overrides JSON
        self.assertEqual(cm.get_api_url(), "http://cli-api.com")
        # cache_duration: JSON (CLI did not provide)
        self.assertEqual(cm.get_cache_duration(), 1000)
        # yolo_model_path: CLI (JSON did not provide)
        self.assertEqual(cm.get_yolo_model_path(), "cli_yolo.pt")
        # keep_split_card_images: CLI overrides default
        self.assertEqual(cm.get_keep_split_card_images(), True)

        # log_file_name: Default (neither CLI nor JSON provided)
        self.assertEqual(cm.get_log_file_name(), self.cm_defaults["log_file_name"])
        # history_file_path: Default name, path constructed with CLI output_path
        expected_history_path = os.path.join("cli_output_final/", "data", self.cm_defaults["history_file_name"])
        self.assertEqual(cm.get_history_file_path(), expected_history_path)

        # image_preprocessing_settings: From JSON, check one overridden and one default from base default
        ips = cm.get_image_preprocessing_settings()
        self.assertEqual(ips["contrast_check_threshold"], 0.50) # From JSON
        self.assertEqual(ips["ocr_preprocessing"]["clahe_clip_limit"], 2.5) # From JSON
        # Check a default value that wasn't in JSON to ensure merge/override logic is as expected
        # (Current logic: if "image_preprocessing_settings" is in JSON, it replaces the whole default dict)
        self.assertEqual(ips.get("illumination_clip_limit"),
                         self.cm_defaults["image_preprocessing_settings"]["illumination_clip_limit"]) # Should be default

        # crawl_directories: Default (neither CLI nor JSON provided)
        self.assertEqual(cm.get_crawl_directories(), self.cm_defaults["crawl_directories"])

    def test_06_history_file_path_construction_no_output_path(self):
        """Test history_file_path construction when output_path is not set."""
        # No config file, no CLI args for output_path
        cm = ConfigManager(config_file=os.path.join(self.test_dir.name, "non_existent_config.json"), cli_args=argparse.Namespace(config_file=None))
        # Expect history_file_path to be relative to CWD's "data" subdir
        self.assertEqual(cm.get_history_file_path(), self.default_history_base_path)

        # With history_file_name in config.json, but still no output_path
        json_data = {"history_file_name": "custom_history.log"}
        config_file_path = self._create_dummy_config_file(json_data)
        cm_json = ConfigManager(config_file=config_file_path, cli_args=argparse.Namespace(config_file=None))
        expected_path = os.path.join("data", "custom_history.log")
        self.assertEqual(cm_json.get_history_file_path(), expected_path)

        # With history_file_path fully specified in config.json (overrides construction)
        json_data_full_path = {"history_file_path": "/custom/path/to/history.log"}
        config_file_path_full = self._create_dummy_config_file(json_data_full_path)
        cm_json_full = ConfigManager(config_file=config_file_path_full, cli_args=argparse.Namespace(config_file=None))
        self.assertEqual(cm_json_full.get_history_file_path(), "/custom/path/to/history.log")

    def test_07_empty_config_file(self):
        """Test behavior with an empty JSON config file (e.g., {})."""
        config_file_path = self._create_dummy_config_file({})
        cm = ConfigManager(config_file=config_file_path, cli_args=None)
        # All values should be their ConfigManager defaults
        self.assertEqual(cm.get_api_url(), self.cm_defaults["api_url"])
        self.assertEqual(cm.get_yolo_model_path(), self.cm_defaults["yolo_model_path"])
        self.assertEqual(cm.get_crawl_directories(), self.cm_defaults["crawl_directories"])

    def test_08_config_file_not_found_silent_fail(self):
        """Test that a non-existent config file logs a warning but uses defaults/CLI."""
        # Logger is part of ConfigManager, so we can't easily check log output here
        # without more complex mocking. This test primarily ensures it doesn't crash.
        cli_args = argparse.Namespace(output_dir="cli_output_for_missing_file/", config_file=None)
        cm = ConfigManager(config_file="non_existent_config.json", cli_args=cli_args)
        self.assertEqual(cm.get_output_path(), "cli_output_for_missing_file/")
        self.assertEqual(cm.get_api_url(), self.cm_defaults["api_url"]) # Should be default

    def test_09_invalid_json_file(self):
        """Test behavior with an invalid JSON config file."""
        invalid_json_path = os.path.join(self.test_dir.name, "invalid.json")
        with open(invalid_json_path, "w") as f:
            f.write("this is not json")

        # This should log an error but not crash, and proceed with defaults/CLI
        cli_args = argparse.Namespace(output_dir="cli_output_for_invalid_json/", config_file=None)
        cm = ConfigManager(config_file=invalid_json_path, cli_args=cli_args)
        self.assertEqual(cm.get_output_path(), "cli_output_for_invalid_json/")
        self.assertEqual(cm.get_api_url(), self.cm_defaults["api_url"]) # Default

    def test_10_image_preprocessing_settings_merging_logic(self):
        """
        Test how image_preprocessing_settings from JSON and defaults are handled.
        Current ConfigManager behavior: if "image_preprocessing_settings" is in JSON,
        it *replaces* the entire default dictionary for this key.
        """
        # Default IPS for reference
        default_ips = ConfigManager.DEFAULT_IMAGE_PREPROCESSING_SETTINGS.copy()

        # Scenario 1: JSON provides a partial IPS override
        json_data_partial_ips = {
            "image_preprocessing_settings": {
                "contrast_check_threshold": 0.99, # Override one value
                "new_ocr_setting": True # Add a new value within ocr_preprocessing
            }
        }
        config_file_path_partial = self._create_dummy_config_file(json_data_partial_ips)
        cm_partial = ConfigManager(config_file=config_file_path_partial)

        retrieved_ips_partial = cm_partial.get_image_preprocessing_settings()
        # Check that the JSON value for contrast_check_threshold is used
        self.assertEqual(retrieved_ips_partial["contrast_check_threshold"], 0.99)
        # Check that the new_ocr_setting is present
        self.assertEqual(retrieved_ips_partial["new_ocr_setting"], True)
        # Check that a key from the original defaults that wasn't in this JSON is now GONE
        # because the entire dict is replaced.
        self.assertNotIn("illumination_clip_limit", retrieved_ips_partial)
        self.assertNotIn("ocr_preprocessing", retrieved_ips_partial) # The whole ocr_preprocessing dict from default is gone

        # Scenario 2: JSON does NOT provide image_preprocessing_settings
        json_data_no_ips = {"api_url": "http://someurl.com"}
        config_file_path_no_ips = self._create_dummy_config_file(json_data_no_ips)
        cm_no_ips = ConfigManager(config_file=config_file_path_no_ips)

        retrieved_ips_no = cm_no_ips.get_image_preprocessing_settings()
        # Should be the full default dictionary from ConfigManager
        self.assertEqual(retrieved_ips_no, default_ips)


if __name__ == "__main__":
    unittest.main()
