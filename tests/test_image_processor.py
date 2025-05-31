import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import os # For os.path.abspath

from src.core.image_processor import process_images
from src.app.config_manager import ConfigManager # For creating mock instances
from src.core.exceptions import ImageProcessingError, FileNotFoundError # FileNotFoundError is a builtin but good to be explicit

class TestImageProcessor(unittest.TestCase):
    """Tests for the process_images function."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        # Setup default return values for config manager getters used by process_images or its callees
        self.mock_config_manager.get_yolo_model_path.return_value = "dummy_model.pt"
        self.mock_config_manager.get_segmentation_confidence_threshold.return_value = 0.5
        # CardSegmenter uses these for saving, process_images doesn't directly use them anymore
        self.mock_config_manager.get_save_segmented_images.return_value = False
        self.mock_config_manager.get_save_segmented_images_path.return_value = "dummy_output/segmented"
        # For OCR preprocessing parameters within CardSegmenter
        self.mock_config_manager.get_image_preprocessing_settings.return_value = {
            "ocr_preprocessing": {
                "clahe_clip_limit": 2.0, "clahe_tile_grid_size": [8,8],
                "median_blur_ksize": 3, "adaptive_thresh_block_size": 11, "adaptive_thresh_C": 2
            }
        }


        self.dummy_image_content = np.zeros((100, 100, 3), dtype=np.uint8)
        self.image_files = ["valid_image1.jpg", "valid_image2.png"]

        # Make image_files absolute for the os.path.exists checks
        self.abs_image_files = [os.path.abspath(f) for f in self.image_files]


    @patch('src.core.image_processor.cv2.imread')
    @patch('src.core.image_processor.run_inference') # Patches run_inference in image_processor's scope
    @patch('src.core.image_processor.CardSegmenter') # Patches CardSegmenter in image_processor's scope
    @patch('src.core.image_processor.os.path.exists') # Patch os.path.exists used in process_images
    def test_process_images_success(self, mock_path_exists, mock_card_segmenter_constructor, mock_run_inference, mock_cv_imread):
        """Test process_images with valid image files and successful processing."""
        mock_path_exists.return_value = True # All image files exist
        mock_cv_imread.return_value = self.dummy_image_content # Simulate successful image read

        # Mock CardSegmenter instance and its methods if necessary (though run_inference is the direct call now)
        mock_segmenter_instance = MagicMock()
        mock_card_segmenter_constructor.return_value = mock_segmenter_instance

        # Mock run_inference to return some dummy segmentation data
        dummy_segmentation_output = [{"name": "Card A", "confidence": 0.9, "bbox": [0,0,10,10]}]
        mock_run_inference.return_value = dummy_segmentation_output

        result = process_images(
            self.image_files,
            "dummy_output_path_context",
            self.mock_config_manager # Pass the mock ConfigManager
        )

        self.assertEqual(len(result), len(self.image_files))
        for i, item in enumerate(result):
            self.assertEqual(item["image_path"], self.image_files[i])
            self.assertEqual(item["segmentations"], dummy_segmentation_output)

        # Check that CardSegmenter was initialized with the config_manager
        mock_card_segmenter_constructor.assert_called_once_with(config_manager=self.mock_config_manager)

        # Check that run_inference was called for each image with the correct segmenter and confidence
        expected_confidence = self.mock_config_manager.get_segmentation_confidence_threshold()
        calls = [
            call(self.dummy_image_content, mock_segmenter_instance, expected_confidence),
            call(self.dummy_image_content, mock_segmenter_instance, expected_confidence)
        ]
        mock_run_inference.assert_has_calls(calls)
        self.assertEqual(mock_run_inference.call_count, len(self.image_files))

        # Check cv2.imread calls
        abs_calls = [call(os.path.abspath(f)) for f in self.image_files]
        mock_cv_imread.assert_has_calls(abs_calls)


    @patch('src.core.image_processor.os.path.exists', return_value=False) # Simulate file not existing
    def test_process_images_file_not_found(self, mock_path_exists):
        """Test process_images raises FileNotFoundError if an image file does not exist."""
        with self.assertRaises(FileNotFoundError) as context:
            process_images(
                self.image_files,
                "dummy_output",
                self.mock_config_manager
            )
        # Check that the error message contains the path of the first file it couldn't find
        self.assertIn(os.path.abspath(self.image_files[0]), str(context.exception))
        mock_path_exists.assert_called_once_with(os.path.abspath(self.image_files[0]))


    @patch('src.core.image_processor.os.path.exists', return_value=True)
    @patch('src.core.image_processor.cv2.imread', return_value=None) # Simulate cv2.imread failing
    def test_process_images_imread_fails(self, mock_cv_imread, mock_path_exists):
        """Test process_images raises ImageProcessingError if cv2.imread returns None."""
        with self.assertRaises(ImageProcessingError) as context:
            process_images(
                self.image_files,
                "dummy_output",
                self.mock_config_manager
            )
        self.assertIn("Could not read image", str(context.exception))
        self.assertIn(os.path.abspath(self.image_files[0]), str(context.exception))


    @patch('src.core.image_processor.cv2.imread', return_value=np.zeros((100,100,3), dtype=np.uint8))
    @patch('src.core.image_processor.run_inference')
    @patch('src.core.image_processor.CardSegmenter')
    @patch('src.core.image_processor.os.path.exists', return_value=True)
    def test_process_images_run_inference_error(self, mock_path_exists, mock_card_segmenter_constructor, mock_run_inference, mock_cv_imread):
        """Test process_images propagates ImageProcessingError from run_inference (wrapped)."""
        mock_run_inference.side_effect = RuntimeError("Simulated inference crash") # run_inference might raise various things

        with self.assertRaises(ImageProcessingError) as context: # process_images should wrap it
            process_images(
                self.image_files,
                "dummy_output",
                self.mock_config_manager
            )
        self.assertIn("Simulated inference crash", str(context.exception))
        self.assertIn(f"An unexpected error occurred during processing of {self.image_files[0]}", str(context.exception))


    @patch('src.core.image_processor.cv2.imread', side_effect=cv2.error("OpenCV Read Error"))
    @patch('src.core.image_processor.os.path.exists', return_value=True)
    def test_process_images_cv2_error_on_read(self, mock_path_exists, mock_cv_imread):
        """Test process_images wraps cv2.error during imread into ImageProcessingError."""
        with self.assertRaises(ImageProcessingError) as context:
            process_images(
                self.image_files,
                "dummy_output",
                self.mock_config_manager
            )
        self.assertIn("OpenCV error processing image", str(context.exception))
        self.assertIn(self.image_files[0], str(context.exception))


if __name__ == '__main__':
    unittest.main()
