import unittest
import os
import shutil
from unittest.mock import patch, mock_open, call
from cli import parse_arguments
from config_manager import ConfigManager
import main  # Import the main module to access its logic

class TestCLI(unittest.TestCase):
    def test_required_arguments(self):
        with self.assertRaises(SystemExit):  # Assuming argparse uses SystemExit for errors
            parse_arguments()  # No arguments provided

        with self.assertRaises(SystemExit):
            parse_arguments(["input_dir"])  # Only one argument

        # Test with both required arguments
        args = parse_arguments(["input_dir", "output_dir"])
        self.assertEqual(args.input_dir, "input_dir")
        self.assertEqual(args.output_dir, "output_dir")

    def test_optional_arguments(self):
        args = parse_arguments(["input_dir", "output_dir", "--keep_split_card_images"])
        self.assertTrue(args.keep_split_card_images)

        args = parse_arguments(["input_dir", "output_dir", "--crawl_directories"])
        self.assertTrue(args.crawl_directories)

    def test_default_crawl_directories(self):
        args = parse_arguments(["input_dir", "output_dir"])
        self.assertTrue(args.crawl_directories)

class TestHistoryLog(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.history_file = os.path.join("data", "processed_images.log")  # Updated history file path

    def tearDown(self):
        shutil.rmtree(self.output_dir)
        # Updated history file path and handling for potential non-existence
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_log_creation(self, mock_file, mock_exists):
        # Simulate running the program and check if history file is created
        config_manager = ConfigManager(cli_args={"output_dir": self.output_dir, "input_dir": "dummy_input"})
        with patch("main.config_manager", config_manager):
            main.main()
        mock_file.assert_called_once_with(self.history_file, "w")

    @patch("os.path.exists", return_value=False)  # Ensure no existing history for a clean test
    @patch("builtins.open", new_callable=mock_open)
    @patch("image_reader.read_images_from_folder", return_value=["image1.jpg", "image2.png"])
    def test_image_tracking(self, mock_read_images, mock_file, mock_exists):
        config_manager = ConfigManager(cli_args={"output_dir": self.output_dir, "input_dir": "dummy_input"})
        with patch("main.config_manager", config_manager):
            main.main()
        # Check the written content (should be image filenames + newline)
        handle = mock_file()
        handle.write.assert_has_calls([call("image1.jpg\n"), call("image2.png\n")], any_order=False)

    @patch("os.path.exists", side_effect=lambda path: path == os.path.join("data", "processed_images.log"))  # Updated path
    @patch("builtins.open", new_callable=mock_open, read_data="image1.jpg\n")  # "image1.jpg" already in history
    @patch("image_reader.read_images_from_folder", return_value=["image1.jpg", "image2.png"])
    def test_duplicate_skipping(self, mock_read_images, mock_file, mock_exists):
        config_manager = ConfigManager(cli_args={"output_dir": self.output_dir, "input_dir": "dummy_input"})
        with patch("main.config_manager", config_manager):
            main.main()
        # Check the written content (should only be "image2.png")
        handle = mock_file()
        calls = [call("image1.jpg\n"), call("image2.png\n")]  # History file is opened in "read" then "append" mode
        handle.write.assert_has_calls([call("image2.png\n")], any_order=False)  # only "image2.png" should be written

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("image_reader.read_images_from_folder", return_value=["image3.jpg", "image4.png"])
    def test_history_file_in_data_dir(self, mock_read_images, mock_file, mock_exists):
        history_file_path = os.path.join("data", "processed_images.log")  # Updated path
        config_manager = ConfigManager(cli_args={"output_dir": self.output_dir, "input_dir": "dummy_input"})
        with patch("main.config_manager", config_manager):
            main.main()

        mock_exists.assert_called_with(history_file_path)
        handle = mock_file()
        file_calls = [call(history_file_path, 'r'), call(history_file_path, 'a')]
        mock_file.assert_has_calls(file_calls, any_order=True)
        handle.write.assert_has_calls([call("image3.jpg\n"), call("image4.png\n")], any_order=False)

    def test_duplicate_imports_avoided(self):
        # Create a dummy input directory with image files
        input_dir = "test_input"
        os.makedirs(input_dir, exist_ok=True)
        image_files = ["image1.jpg", "image2.png"]
        for image_file in image_files:
            with open(os.path.join(input_dir, image_file), "w") as f:
                f.write("dummy content")

        # Run the application for the first time
        config_manager = ConfigManager(cli_args={"input_dir": input_dir, "output_dir": self.output_dir})
        with patch("main.config_manager", config_manager):
            main.main()

        # Check if the history file contains the image paths
        history_file_path = os.path.join("data", "processed_images.log")
        with open(history_file_path, "r") as f:
            processed_images = [line.strip() for line in f]
        expected_images = [os.path.abspath(os.path.join(input_dir, image_file)) for image_file in image_files]
        self.assertEqual(processed_images, expected_images)

        # Get the last modified timestamp of the history file
        initial_timestamp = os.path.getmtime(history_file_path)

        # Run the application for the second time
        with patch("main.config_manager", config_manager):
            main.main()

        # Check if the history file remains unchanged
        final_timestamp = os.path.getmtime(history_file_path)
        self.assertEqual(initial_timestamp, final_timestamp)

        # Clean up the dummy input directory
        shutil.rmtree(input_dir)

if __name__ == "__main__":
    unittest.main()
