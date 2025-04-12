import unittest
import numpy as np
from src.core.card_segmenter import CardSegmenter

class TestCardSegmenter(unittest.TestCase):
    def test_segment_cards_no_detection(self):
        # Mock the YOLO model to return empty results
        class MockYOLO:
            def __init__(self, model_path):
                pass
            def predict(self, image):
                return []

        # Patch the YOLO class in CardSegmenter
        with unittest.mock.patch("card_segmenter.YOLO", MockYOLO):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = segmenter.segment_cards(image)
            self.assertEqual(results, [])

    def test_segment_cards_with_detection(self):
        # Mock the YOLO model to return dummy results
        class MockYOLO:
            def __init__(self, model_path):
                pass
            def predict(self, image):
                class MockResults:
                    def __init__(self):
                        self.masks = MockMasks()
                        self.boxes = MockBoxes()
                class MockMasks:
                    def __init__(self):
                        self.data = MockData()
                class MockBoxes:
                    def __init__(self):
                        self.xyxy = MockData()
                class MockData:
                    def cpu(self):
                        return self
                    def numpy(self):
                        return [np.zeros((100, 100), dtype=np.uint8)], [[10, 10, 90, 90]]
                return [MockResults()]

        # Patch the YOLO class in CardSegmenter
        with unittest.mock.patch("card_segmenter.YOLO", MockYOLO):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = segmenter.segment_cards(image)
            self.assertEqual(len(results), 1)
            self.assertIn("mask", results[0])
            self.assertIn("bbox", results[0])
            self.assertEqual(results[0]["mask"].shape, (100, 100))
            self.assertEqual(results[0]["bbox"], [10, 10, 90, 90])

    def test_segment_cards_error_handling(self):
        # Mock the YOLO model to raise an exception
        class MockYOLO:
            def __init__(self, model_path):
                pass
            def predict(self, image):
                raise Exception("Segmentation error")

        # Patch the YOLO class in CardSegmenter
        with unittest.mock.patch("card_segmenter.YOLO", MockYOLO):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = segmenter.segment_cards(image)
            self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
