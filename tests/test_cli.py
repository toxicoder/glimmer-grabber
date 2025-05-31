import unittest
from unittest.mock import patch, MagicMock, mock_open, call # Added call
import argparse
import os # For os.path.join

# Import the main function from cli.py and other necessary components
from src.app.cli import main as cli_main
# We will be mocking these, so direct imports are for type hinting or isinstance checks if needed.
from src.app.cli_args_parser import CLIArgsParser
from src.app.config_manager import ConfigManager
from src.app.image_reader import read_images_from_folder
from src.core.image_processor import process_images
from src.app.card_data_fetcher import CardDataFetcher
from src.app.cli import generate_csv # For direct patching if needed, or check calls on it
# Import custom exceptions to test for them
from src.app.exceptions import APIFetchError, CacheError, DataFormatError
from src.core.exceptions import ImageProcessingError
# FileNotFoundError is a built-in, but good to be explicit for testing its handling
# from builtins import FileNotFoundError # Not needed for import if just catching


class TestCLI(unittest.TestCase):
    """Tests for the main CLI application flow in src.app.cli.main."""

    # Centralized mock setup for CLIArgsParser and ConfigManager arguments
    def _setup_common_mocks(self, mock_cli_args_parser_constructor, mock_config_manager_constructor):
        mock_cli_args_instance = MagicMock(spec=CLIArgsParser)
        mock_cli_args_instance.parse_arguments.return_value = argparse.Namespace(
            input_dir="test_input",
            output_dir="test_output", # This will be used for initial log setup
            config_file=None,
            api_url=None, yolo_model_path=None, cache_duration=None,
            segmentation_confidence_threshold=None, history_file_path=None,
            keep_split_card_images=False, crawl_directories=True,
            save_segmented_images=False, save_segmented_images_path=None
        )
        mock_cli_args_parser_constructor.return_value = mock_cli_args_instance

        mock_cm_instance = MagicMock(spec=ConfigManager)
        mock_cm_instance.get_input_path.return_value = "test_input"
        mock_cm_instance.get_output_path.return_value = "test_output" # Definitive output path
        mock_cm_instance.get_log_file_name.return_value = "app_test.log"

        self.expected_history_path = os.path.join("test_output", "data", "default_history.log")
        # Mock get_history_file_path to return a predictable, absolute path
        # This now uses get_output_path and get_history_file_name internally in ConfigManager
        mock_cm_instance.get_history_file_name.return_value = "default_history.log" # Used by get_history_file_path
        mock_cm_instance.get_history_file_path.return_value = self.expected_history_path

        mock_cm_instance.get_keep_split_card_images.return_value = False
        mock_cm_instance.get_crawl_directories.return_value = True
        mock_cm_instance.get_save_segmented_images.return_value = False
        mock_cm_instance.get_save_segmented_images_path.return_value = None
        mock_cm_instance.get_api_url.return_value = "http://fakeapi.com"
        mock_cm_instance.get_cache_duration.return_value = 3600
        mock_cm_instance.get_cache_file_name.return_value = "api_cache_test.json"
        mock_cm_instance.get_yolo_model_path.return_value = "test_model.pt"
        mock_cm_instance.get_segmentation_confidence_threshold.return_value = 0.55
        mock_cm_instance.get_image_preprocessing_settings.return_value = {} # Default empty
        mock_cm_instance.actual_config_file_path_used = os.path.abspath(ConfigManager.DEFAULT_CONFIG_FILE)
        mock_config_manager_constructor.return_value = mock_cm_instance

        return mock_cli_args_instance, mock_cm_instance


    @patch('src.app.cli.generate_csv')
    @patch('src.app.cli.CardDataFetcher')
    @patch('src.app.cli.process_images')
    @patch('src.app.cli.read_images_from_folder')
    @patch('src.app.cli.load_processed_images')
    @patch('src.app.cli.setup_logging')
    @patch('src.app.cli.ConfigManager')
    @patch('src.app.cli.CLIArgsParser')
    def test_main_successful_flow(
        self, mock_cli_args_parser_constructor, mock_config_manager_constructor,
        mock_setup_logging, mock_load_processed_images, mock_read_images,
        mock_process_images, mock_card_data_fetcher_constructor, mock_generate_csv
    ):
        """Test a successful run of cli_main with typical operations."""

        mock_cli_args_instance, mock_cm_instance = self._setup_common_mocks(
            mock_cli_args_parser_constructor, mock_config_manager_constructor
        )

        # Setup return values for other mocked functions
        mock_load_processed_images.return_value = ["img_already_done.jpg"] # Some history
        mock_read_images.return_value = [os.path.abspath("test_input/img1.jpg"), os.path.abspath("test_input/img2.png")]

        mock_processed_data_val = [
            {"image_path": "test_input/img1.jpg", "segmentations": [{"name": "Card X", "confidence": 0.9}]},
            {"image_path": "test_input/img2.png", "segmentations": [{"name": "Card Y", "confidence": 0.8}]}
        ]
        mock_process_images.return_value = mock_processed_data_val

        mock_fetcher_instance = MagicMock(spec=CardDataFetcher)
        mock_fetched_api_data_val = [
            {"name": "Card X", "type": "TypeA", "set": "Set1", "extracted_card_name": "Card X"},
            {"name": "Card Y", "type": "TypeB", "set": "Set2", "extracted_card_name": "Card Y"}
        ]
        mock_fetcher_instance.fetch_card_data.return_value = mock_fetched_api_data_val
        mock_card_data_fetcher_constructor.return_value = mock_fetcher_instance

        cli_main() # Execute the main function

        # Assertions
        mock_cli_args_parser_constructor.assert_called_once()
        mock_cli_args_instance.parse_arguments.assert_called_once()

        mock_config_manager_constructor.assert_called_once_with(
            config_file=None, # From mock_cli_args_instance
            cli_args=mock_cli_args_instance.parse_arguments.return_value
        )

        mock_setup_logging.assert_called_once_with("test_output", "app_test.log")
        mock_load_processed_images.assert_called_once_with(self.expected_history_path)
        mock_read_images.assert_called_once()

        # Check that only new images are processed
        # img1.jpg basename is "img1.jpg", img2.png basename is "img2.png"
        # history has "img_already_done.jpg"
        # So, both img1.jpg and img2.png are new.
        expected_files_to_process = [os.path.abspath("test_input/img1.jpg"), os.path.abspath("test_input/img2.png")]
        mock_process_images.assert_called_once_with(
            expected_files_to_process,
            "test_output", # output_path from config
            mock_cm_instance
        )

        expected_card_names_for_fetcher = ["Card X", "Card Y"]
        expected_cache_file_path = os.path.join("test_output", "api_cache_test.json")
        mock_card_data_fetcher_constructor.assert_called_once_with(
            config_manager=mock_cm_instance,
            cache_file=expected_cache_file_path
        )
        mock_fetcher_instance.fetch_card_data.assert_called_once_with(expected_card_names_for_fetcher)
        mock_generate_csv.assert_called_once_with(mock_fetched_api_data_val, "test_output")

    @patch('src.app.cli.logger') # To verify logging calls for specific scenarios
    @patch('src.app.cli.read_images_from_folder', return_value=[]) # No images found
    @patch('src.app.cli.load_processed_images', return_value=[])
    @patch('src.app.cli.setup_logging')
    @patch('src.app.cli.ConfigManager')
    @patch('src.app.cli.CLIArgsParser')
    def test_main_no_images_found(
        self, mock_cli_args_parser_constructor, mock_config_manager_constructor,
        mock_setup_logging, mock_load_processed, mock_read_images, mock_cli_logger
    ):
        """Test cli_main when read_images_from_folder returns an empty list."""
        _, mock_cm_instance = self._setup_common_mocks(
            mock_cli_args_parser_constructor, mock_config_manager_constructor
        )

        cli_main()
        # Check that specific info message is logged
        mock_cli_logger.info.assert_any_call("No new images to process after checking history.")
        # Ensure processing and beyond are not called
        with patch('src.app.cli.process_images') as mock_proc_img: # Patch here to check not called
            mock_proc_img.assert_not_called()

    @patch('src.app.cli.logger')
    @patch('src.app.cli.process_images', return_value=[{"image_path": "img1.jpg", "segmentations": []}]) # No names extracted
    @patch('src.app.cli.read_images_from_folder', return_value=["img1.jpg"])
    @patch('src.app.cli.load_processed_images', return_value=[])
    @patch('src.app.cli.setup_logging')
    @patch('src.app.cli.ConfigManager')
    @patch('src.app.cli.CLIArgsParser')
    def test_main_no_card_names_extracted(
        self, mock_cli_args_parser_constructor, mock_config_manager_constructor,
        mock_setup_logging, mock_load_processed, mock_read_images, mock_process_images, mock_cli_logger
    ):
        """Test cli_main when no card names are extracted from images."""
        _, mock_cm_instance = self._setup_common_mocks(
            mock_cli_args_parser_constructor, mock_config_manager_constructor
        )

        cli_main()
        mock_cli_logger.info.assert_any_call("No card names were extracted from the processed images. Nothing to fetch.")
        with patch('src.app.cli.CardDataFetcher') as mock_cdf_constructor: # Patch here to check not called
            mock_cdf_constructor.assert_not_called()

    @patch('src.app.cli.logger')
    @patch('src.app.cli.read_images_from_folder', side_effect=FileNotFoundError("Mocked File Access Denied"))
    @patch('src.app.cli.setup_logging')
    @patch('src.app.cli.ConfigManager')
    @patch('src.app.cli.CLIArgsParser')
    def test_main_handles_known_exceptions(
        self, mock_cli_args_parser_constructor, mock_config_manager_constructor,
        mock_setup_logging, mock_read_images_error, mock_cli_logger
    ):
        """Test cli_main catches and logs known application exceptions."""
        _, mock_cm_instance = self._setup_common_mocks(
            mock_cli_args_parser_constructor, mock_config_manager_constructor
        )

        cli_main()

        # Check that the error was logged correctly (message contains the exception's message)
        # This relies on the logger.error call in cli.main's except block
        error_logged = any(
            "A known application error occurred: Mocked File Access Denied" in str(call_args)
            for call_args in mock_cli_logger.error.call_args_list
        )
        self.assertTrue(error_logged, "Known exception (FileNotFoundError) was not logged as expected.")

    @patch('src.app.cli.logger')
    @patch('src.app.cli.read_images_from_folder', side_effect=Exception("Very Unexpected Crash!"))
    @patch('src.app.cli.setup_logging')
    @patch('src.app.cli.ConfigManager')
    @patch('src.app.cli.CLIArgsParser')
    def test_main_handles_unexpected_exceptions(
        self, mock_cli_args_parser_constructor, mock_config_manager_constructor,
        mock_setup_logging, mock_read_images_error, mock_cli_logger
    ):
        """Test cli_main catches and logs unexpected generic exceptions."""
        _, mock_cm_instance = self._setup_common_mocks(
            mock_cli_args_parser_constructor, mock_config_manager_constructor
        )

        cli_main()

        # Check that logger.exception was called for the unexpected error
        exception_logged = any(
            "An unexpected critical error occurred in the main application flow:" in str(call_args)
            for call_args in mock_cli_logger.exception.call_args_list
        )
        self.assertTrue(exception_logged, "Unexpected exception was not logged via logger.exception.")


if __name__ == "__main__":
    unittest.main()
