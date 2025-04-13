import unittest
from unittest.mock import patch, MagicMock
from src.core.image_processor import process_images

class TestImageProcessor(unittest.TestCase):

    @patch("cv2.imread")
    def test_process_images_valid_files(self, mock_imread):
        # Test case for valid image files
        mock_imread.return_value = MagicMock()  # Simulate a successful image read
        with patch("src.core.card_segmenter.CardSegmenter.segment_cards") as mock_segment_cards:
            mock_segment_cards.return_value = "dummy_segmentation_data"
            image_files = ["valid_image1.jpg", "valid_image2.png"]
            output_path = "output"
            result = process_images(image_files, output_path, False, "")
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["image_path"], "valid_image1.jpg")
            self.assertEqual(result[0]["segmentations"], "dummy_segmentation_data")
            self.assertEqual(result[1]["image_path"], "valid_image2.png")
            self.assertEqual(result[1]["segmentations"], "dummy_segmentation_data")

    @patch("cv2.imread")
    def test_process_images_invalid_files(self, mock_imread):
        # Test case for invalid image files
        mock_imread.return_value = None  # Simulate an unsuccessful image read
        image_files = ["invalid_image1.xyz", "invalid_image2.abc"]
        output_path = "output"
        result = process_images(image_files, output_path, False, "")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["image_path"], "invalid_image1.xyz")
        self.assertIsNone(result[0]["segmentations"])
        self.assertEqual(result[1]["image_path"], "invalid_image2.abc")
        self.assertIsNone(result[1]["segmentations"])

    @patch("cv2.imread")
    def test_process_images_mixed_files(self, mock_imread):
        # Test case for a mix of valid and invalid files
        mock_imread.side_effect = [MagicMock(), None, MagicMock()]  # Simulate mixed results
        with patch("src.core.card_segmenter.CardSegmenter.segment_cards") as mock_segment_cards:
            mock_segment_cards.return_value = "dummy_segmentation_data"
            image_files = ["valid_image.jpg", "invalid_image.xyz", "another_valid_image.png"]
            output_path = "output"
            result = process_images(image_files, output_path, False, "")
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["image_path"], "valid_image.jpg")
            self.assertEqual(result[0]["segmentations"], "dummy_segmentation_data")
            self.assertEqual(result[1]["image_path"], "invalid_image.xyz")
            self.assertIsNone(result[1]["segmentations"])
            self.assertEqual(result[2]["image_path"], "another_valid_image.png")
            self.assertEqual(result[2]["segmentations"], "dummy_segmentation_data")

if __name__ == '__main__':
    unittest.main()
