import unittest
import numpy as np
from unittest.mock import patch, MagicMock # Use MagicMock for segmenter instance

from src.core.inference import run_inference
from src.core.card_segmenter import CardSegmenter # For type hinting and mocking
from src.app.config_manager import ConfigManager # For mock config if CardSegmenter needs it

class TestInference(unittest.TestCase):
    """Tests for the run_inference function."""

    def setUp(self):
        """Set up test environment."""
        self.dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.dummy_original_image_path = "dummy_path/image.jpg"

        # Mock ConfigManager that CardSegmenter might use if it creates its own
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        self.mock_config_manager.get_yolo_model_path.return_value = "dummy_model.pt"
        self.mock_config_manager.get_image_preprocessing_settings.return_value = {
            "ocr_preprocessing": {}
        }
        self.mock_config_manager.get_save_segmented_images.return_value = False

        # Mock CardSegmenter instance
        self.mock_segmenter = MagicMock(spec=CardSegmenter)
        # Configure the mock_segmenter to have a config_manager attribute,
        # as the real CardSegmenter would. This is for completeness if any
        # methods on mock_segmenter were to try to access it, though for these tests,
        # we primarily mock segment_cards.
        self.mock_segmenter.config_manager = self.mock_config_manager


    def test_run_inference_no_detections_from_segmenter(self):
        """Test run_inference when the segmenter returns no detections."""
        self.mock_segmenter.segment_cards.return_value = []

        results = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.5,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(results, [])
        self.mock_segmenter.segment_cards.assert_called_once_with(self.dummy_image, self.dummy_original_image_path)

    def test_run_inference_detection_above_threshold(self):
        """Test when a detection's confidence is above the threshold."""
        mock_detection_results = [
            {"name": "Card Alpha", "confidence": 0.8, "bbox": [10, 10, 90, 90], "mask": MagicMock(), "image": MagicMock()}
        ]
        self.mock_segmenter.segment_cards.return_value = mock_detection_results

        results = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.7,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Card Alpha")
        self.mock_segmenter.segment_cards.assert_called_once_with(self.dummy_image, self.dummy_original_image_path)

    def test_run_inference_detection_below_threshold(self):
        """Test when a detection's confidence is below the threshold."""
        mock_detection_results = [
            {"name": "Card Beta", "confidence": 0.3, "bbox": [10, 10, 90, 90], "mask": MagicMock(), "image": MagicMock()}
        ]
        self.mock_segmenter.segment_cards.return_value = mock_detection_results

        results = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.4,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(results, [])
        self.mock_segmenter.segment_cards.assert_called_once_with(self.dummy_image, self.dummy_original_image_path)

    def test_run_inference_detection_at_threshold(self):
        """Test when a detection's confidence is exactly at the threshold."""
        mock_detection_results = [
            {"name": "Card Gamma", "confidence": 0.5, "bbox": [10, 10, 90, 90], "mask": MagicMock(), "image": MagicMock()}
        ]
        self.mock_segmenter.segment_cards.return_value = mock_detection_results

        results = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.5,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Card Gamma")

    def test_run_inference_multiple_detections_mixed_confidence(self):
        """Test with multiple detections, some above and some below threshold."""
        mock_detection_results = [
            {"name": "HighConf", "confidence": 0.9, "bbox": [10,10,50,50]},
            {"name": "MidConf", "confidence": 0.6, "bbox": [60,60,90,90]},
            {"name": "LowConf", "confidence": 0.2, "bbox": [20,70,80,90]}
        ]
        self.mock_segmenter.segment_cards.return_value = mock_detection_results

        results = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.5,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "HighConf")
        self.assertEqual(results[1]["name"], "MidConf")

    def test_run_inference_segmenter_raises_runtime_error(self):
        """Test run_inference propagates RuntimeError from segmenter."""
        self.mock_segmenter.segment_cards.side_effect = RuntimeError("YOLO crashed")

        with self.assertRaises(RuntimeError) as context:
            run_inference(
                self.dummy_image,
                self.mock_segmenter,
                confidence_threshold=0.5,
                original_image_path=self.dummy_original_image_path
            )
        self.assertIn("YOLO crashed", str(context.exception))

    def test_run_inference_segmenter_raises_other_exception(self):
        """Test run_inference handles general exceptions from segmenter by returning empty list."""
        self.mock_segmenter.segment_cards.side_effect = ValueError("Unexpected value")

        results = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.5,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(results, [])

    def test_run_inference_results_missing_confidence_key(self):
        """Test behavior when segmenter results are missing the 'confidence' key."""
        mock_detection_results = [
            {"name": "NoConfCard", "bbox": [10,10,50,50]}
        ]
        self.mock_segmenter.segment_cards.return_value = mock_detection_results

        results_strict_threshold = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.1,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(results_strict_threshold, [])

        results_zero_threshold = run_inference(
            self.dummy_image,
            self.mock_segmenter,
            confidence_threshold=0.0,
            original_image_path=self.dummy_original_image_path
        )
        self.assertEqual(len(results_zero_threshold), 1)
        self.assertEqual(results_zero_threshold[0]["name"], "NoConfCard")


if __name__ == '__main__':
    unittest.main()
