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
        self.history_file = os.path.join(self.output_dir, "processed_images.txt")

    def tearDown(self):
        shutil.rmtree(self.output_dir)
        if os.path.exists(self.history_file): # Handle cases where test may have failed before deleting
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

    @patch("os.path.exists", side_effect=lambda path: path == os.path.join("test_output", "processed_images.txt"))  # Only history file exists
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

if __name__ == "__main__":
    unittest.main()
