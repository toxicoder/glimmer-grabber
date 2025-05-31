import unittest
from unittest.mock import patch, MagicMock, mock_open, call # Added call
import numpy as np
import tempfile
import os
import cv2 # For imwrite in save_segmented_cards if we test it directly

from src.core.card_segmenter import CardSegmenter
from src.app.config_manager import ConfigManager # For creating mock instances
from src.app.exceptions import ImageProcessingError # Though CardSegmenter might raise RuntimeError

class TestCardSegmenter(unittest.TestCase):
    """Tests for the CardSegmenter class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

        # Default mock ConfigManager
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        self.mock_config_manager.get_yolo_model_path.return_value = "dummy_model.pt"
        self.mock_config_manager.get_save_segmented_images.return_value = False # Default to False for most tests
        self.mock_config_manager.get_save_segmented_images_path.return_value = os.path.join(self.test_dir.name, "custom_segmented_output")
        self.mock_config_manager.get_output_path.return_value = self.test_dir.name # For default save path construction

        self.mock_config_manager.get_image_preprocessing_settings.return_value = {
            "ocr_preprocessing": {
                "clahe_clip_limit": 2.0,
                "clahe_tile_grid_size": [8, 8],
                "median_blur_ksize": 3,
                "adaptive_thresh_block_size": 11,
                "adaptive_thresh_C": 2
            }
        }

        self.dummy_image_content = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.putText(self.dummy_image_content, "Test Text", (10,30), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255),1)
        self.dummy_original_image_path = "dummy_path/original_image.jpg"


    def _create_mock_yolo_results_object(self, num_detections=1, with_confidence=True):
        """
        Helper to create a mock YOLO results object (the single element in the list returned by predict).
        """
        mock_result_object = MagicMock()

        if num_detections == 0:
            mock_result_object.masks = None # Or an object where .data.cpu().numpy() is empty
            mock_result_object.boxes = None
            return mock_result_object

        # Mock masks
        mock_masks = MagicMock()
        mask_arrays = []
        for i in range(num_detections):
            mask_array = np.zeros((50, 50), dtype=np.uint8)
            mask_array[10:40, 10+i*5:40+i*5] = 1 # Make masks slightly different
            mask_arrays.append(mask_array)

        mock_masks.data = MagicMock()
        mock_masks.data.cpu.return_value.numpy.return_value = np.array(mask_arrays)
        mock_result_object.masks = mock_masks

        # Mock boxes
        mock_boxes = MagicMock()
        box_arrays = []
        conf_scores_list = []
        for i in range(num_detections):
            box_arrays.append(np.array([10 + i*5, 10 + i*5, 60 + i*5, 60 + i*5], dtype=float))
            if with_confidence:
                conf_scores_list.append(0.9 - i*0.1)

        mock_boxes.xyxy = MagicMock()
        mock_boxes.xyxy.cpu.return_value.numpy.return_value = np.array(box_arrays)

        if with_confidence:
            mock_boxes.conf = MagicMock()
            mock_boxes.conf.cpu.return_value.numpy.return_value = np.array(conf_scores_list, dtype=float)
        else:
            mock_boxes.conf = None

        mock_result_object.boxes = mock_boxes
        return mock_result_object


    @patch('ultralytics.YOLO')
    def test_init_with_config_manager(self, mock_yolo_constructor):
        mock_yolo_model_instance = MagicMock()
        mock_yolo_constructor.return_value = mock_yolo_model_instance

        segmenter = CardSegmenter(config_manager=self.mock_config_manager)

        self.mock_config_manager.get_yolo_model_path.assert_called_once()
        mock_yolo_constructor.assert_called_once_with("dummy_model.pt")
        self.assertIsNotNone(segmenter.model)

    @patch('ultralytics.YOLO')
    @patch('pytesseract.image_to_string', return_value="Detected Card Name")
    @patch('src.core.card_segmenter.cv2.imwrite') # Mock imwrite
    @patch('src.core.card_segmenter.os.makedirs') # Mock makedirs
    def test_segment_cards_saves_individual_images_when_enabled(
        self, mock_makedirs, mock_cv_imwrite, mock_ocr, mock_yolo_constructor
    ):
        """Test segment_cards saves individual images if config is True."""
        # Configure mocks for this test
        self.mock_config_manager.get_save_segmented_images.return_value = True
        # get_save_segmented_images_path already returns self.test_dir.name / "custom_segmented_output"

        mock_yolo_model_instance = MagicMock()
        # model.predict returns a list containing one results object
        mock_yolo_model_instance.predict.return_value = [self._create_mock_yolo_results_object(num_detections=2)]
        mock_yolo_constructor.return_value = mock_yolo_model_instance

        segmenter = CardSegmenter(config_manager=self.mock_config_manager)
        results = segmenter.segment_cards(self.dummy_image_content, self.dummy_original_image_path)

        self.assertEqual(len(results), 2) # Two detections

        # Check os.makedirs was called for the save path
        expected_save_path = os.path.join(self.test_dir.name, "custom_segmented_output")
        mock_makedirs.assert_called_with(expected_save_path, exist_ok=True)

        # Check cv2.imwrite calls
        self.assertEqual(mock_cv_imwrite.call_count, 2)

        # Filename construction: {original_image_name_without_extension}_card_{index}_{card_name}.png
        original_basename = "original_image"
        sanitized_card_name = "Detected_Card_Name" # From mock_ocr and sanitize_filename

        expected_filename1 = os.path.join(expected_save_path, f"{original_basename}_card_0_{sanitized_card_name}.png")
        expected_filename2 = os.path.join(expected_save_path, f"{original_basename}_card_1_{sanitized_card_name}.png")

        # Check first call to imwrite
        call_args1 = mock_cv_imwrite.call_args_list[0][0]
        self.assertEqual(call_args1[0], expected_filename1)
        self.assertIsInstance(call_args1[1], np.ndarray) # Check image data is passed

        # Check second call to imwrite
        call_args2 = mock_cv_imwrite.call_args_list[1][0]
        self.assertEqual(call_args2[0], expected_filename2)
        self.assertIsInstance(call_args2[1], np.ndarray)


    @patch('ultralytics.YOLO')
    @patch('pytesseract.image_to_string', return_value="Card Test")
    @patch('src.core.card_segmenter.cv2.imwrite')
    def test_segment_cards_does_not_save_if_disabled(
        self, mock_cv_imwrite, mock_ocr, mock_yolo_constructor
    ):
        """Test segment_cards does not save images if config is False."""
        self.mock_config_manager.get_save_segmented_images.return_value = False # Explicitly disable

        mock_yolo_model_instance = MagicMock()
        mock_yolo_model_instance.predict.return_value = [self._create_mock_yolo_results_object(num_detections=1)]
        mock_yolo_constructor.return_value = mock_yolo_model_instance

        segmenter = CardSegmenter(config_manager=self.mock_config_manager)
        results = segmenter.segment_cards(self.dummy_image_content, self.dummy_original_image_path)

        self.assertEqual(len(results), 1)
        mock_cv_imwrite.assert_not_called() # Should not be called

    @patch('ultralytics.YOLO')
    @patch('pytesseract.image_to_string', return_value="Card Test")
    @patch('src.core.card_segmenter.cv2.imwrite')
    @patch('src.core.card_segmenter.os.makedirs')
    def test_segment_cards_default_save_path_if_specific_not_set(
        self, mock_makedirs, mock_cv_imwrite, mock_ocr, mock_yolo_constructor
    ):
        """Test that a default save path is used if specific one isn't set but main output_path is."""
        self.mock_config_manager.get_save_segmented_images.return_value = True
        self.mock_config_manager.get_save_segmented_images_path.return_value = None # Simulate not being set
        # self.mock_config_manager.get_output_path() is already set to self.test_dir.name in setUp

        mock_yolo_model_instance = MagicMock()
        mock_yolo_model_instance.predict.return_value = [self._create_mock_yolo_results_object(num_detections=1)]
        mock_yolo_constructor.return_value = mock_yolo_model_instance

        segmenter = CardSegmenter(config_manager=self.mock_config_manager)
        segmenter.segment_cards(self.dummy_image_content, self.dummy_original_image_path)

        expected_default_save_dir = os.path.join(self.test_dir.name, "segmented_cards_default")
        mock_makedirs.assert_called_with(expected_default_save_dir, exist_ok=True)

        original_basename = "original_image"
        sanitized_card_name = "Card_Test"
        expected_filename = os.path.join(expected_default_save_dir, f"{original_basename}_card_0_{sanitized_card_name}.png")
        mock_cv_imwrite.assert_called_once_with(expected_filename, unittest.mock.ANY)

    @patch('ultralytics.YOLO')
    def test_segment_cards_invalid_bbox(self, mock_yolo_constructor):
        """Test that invalid bounding boxes (e.g., out of bounds) are skipped."""
        mock_yolo_model_instance = MagicMock()

        # Create a result object with an invalid bbox
        mock_result_object = MagicMock()
        mock_masks = MagicMock() # Dummy mask
        mask_array = np.zeros((50, 50), dtype=np.uint8)
        mock_masks.data = MagicMock()
        mock_masks.data.cpu.return_value.numpy.return_value = np.array([mask_array])
        mock_result_object.masks = mock_masks

        mock_boxes = MagicMock()
        # Invalid bbox: x2 is outside image width (100)
        invalid_box_array = np.array([[10, 10, 150, 90]], dtype=float)
        mock_boxes.xyxy = MagicMock()
        mock_boxes.xyxy.cpu.return_value.numpy.return_value = invalid_box_array
        mock_boxes.conf = MagicMock() # Add confidence attribute
        mock_boxes.conf.cpu.return_value.numpy.return_value = np.array([0.9], dtype=float)
        mock_result_object.boxes = mock_boxes

        mock_yolo_model_instance.predict.return_value = [mock_result_object]
        mock_yolo_constructor.return_value = mock_yolo_model_instance

        segmenter = CardSegmenter(config_manager=self.mock_config_manager)
        # Patch logger to check for warning
        with patch('src.core.card_segmenter.logger') as mock_card_segmenter_logger:
            results = segmenter.segment_cards(self.dummy_image_content, self.dummy_original_image_path)

        self.assertEqual(len(results), 0) # Invalid bbox should be skipped

        found_warning = False
        for call_arg in mock_card_segmenter_logger.warning.call_args_list:
            if "Bounding box for instance 1 is invalid or out of bounds" in call_arg[0][0]:
                found_warning = True
                break
        self.assertTrue(found_warning, "Warning for invalid bbox not logged.")


if __name__ == '__main__':
    unittest.main()
