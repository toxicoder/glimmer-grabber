import unittest
import numpy as np
from unittest.mock import patch
from inference import run_inference
from card_segmenter import CardSegmenter

class TestInference(unittest.TestCase):
    def test_run_inference_no_detection(self):
        # Mock CardSegmenter to return empty results
        with patch.object(CardSegmenter, "segment_cards", return_value=[]):
            segmenter = CardSegmenter()  # Create an instance (though it will be mocked)
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = run_inference(image, segmenter)
            self.assertEqual(results, [])

    def test_run_inference_with_detection_above_threshold(self):
        # Mock CardSegmenter to return a detection with high confidence
        mock_result = [{"mask": np.zeros((100, 100), dtype=np.uint8), "bbox": [10, 10, 90, 90], "confidence": 0.8}]
        with patch.object(CardSegmenter, "segment_cards", return_value=mock_result):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = run_inference(image, segmenter)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["bbox"], [10, 10, 90, 90])

    def test_run_inference_with_detection_below_threshold(self):
        # Mock CardSegmenter to return a detection with low confidence
        mock_result = [{"mask": np.zeros((100, 100), dtype=np.uint8), "bbox": [10, 10, 90, 90], "confidence": 0.3}]
        with patch.object(CardSegmenter, "segment_cards", return_value=mock_result):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = run_inference(image, segmenter)
            self.assertEqual(results, [])

    def test_run_inference_multiple_detections(self):
        # Mock CardSegmenter to return multiple detections with varying confidences
        mock_results = [
            {"mask": np.zeros((100, 100), dtype=np.uint8), "bbox": [10, 10, 50, 50], "confidence": 0.9},
            {"mask": np.zeros((100, 100), dtype=np.uint8), "bbox": [60, 60, 90, 90], "confidence": 0.6},
            {"mask": np.zeros((100, 100), dtype=np.uint8), "bbox": [20, 70, 80, 90], "confidence": 0.2}
        ]
        with patch.object(CardSegmenter, "segment_cards", return_value=mock_results):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = run_inference(image, segmenter, confidence_threshold=0.5)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["bbox"], [10, 10, 50, 50])
            self.assertEqual(results[1]["bbox"], [60, 60, 90, 90])

    def test_run_inference_error_handling(self):
        # Mock CardSegmenter to raise an exception
        with patch.object(CardSegmenter, "segment_cards", side_effect=Exception("Segmentation error")):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = run_inference(image, segmenter)
            self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
