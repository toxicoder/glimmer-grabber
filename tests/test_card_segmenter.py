import unittest
import numpy as np
from src.core.card_segmenter import CardSegmenter
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import os

class TestCardSegmenter(unittest.TestCase):
    """Tests for the CardSegmenter class."""

    def _create_mock_yolo(self):
        """Helper function to create a mock YOLO model.

        This function creates a MagicMock object that simulates the behavior of the YOLO model,
        returning a predefined set of results upon prediction.
        """
        mock_yolo = MagicMock()
        mock_results = MagicMock()
        mock_masks = MagicMock()
        mock_boxes = MagicMock()
        mock_data = MagicMock()
        mock_data.cpu.return_value = mock_data
        mock_data.numpy.return_value = [np.zeros((100, 100), dtype=np.uint8)], [[10, 10, 90, 90]]
        mock_masks.data = mock_data
        mock_boxes.xyxy = mock_data
        mock_results.masks = mock_masks
        mock_results.boxes = mock_boxes
        mock_yolo.predict.return_value = [mock_results]
        return mock_yolo

    def test_segment_cards_no_detection(self):
        """Test case for when no cards are detected in the image.

        This test verifies that the segment_cards method returns an empty list when the
        mocked YOLO model returns no detections.
        """
        # Mock the YOLO model to return empty results
        mock_yolo = MagicMock()
        mock_yolo.predict.return_value = []

        # Patch the YOLO class in CardSegmenter
        with patch("src.core.card_segmenter.YOLO", return_value=mock_yolo):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = segmenter.segment_cards(image)
            self.assertEqual(results, [])

    def test_segment_cards_with_detection(self):
        """Test case for successful card detection and segmentation.

        This test verifies that the segment_cards method returns a list containing a
        dictionary with the expected keys ('mask', 'bbox') and values when the mocked
        YOLO model returns a detection.
        """
        # Mock the YOLO model to return dummy results
        mock_yolo = self._create_mock_yolo()

        # Patch the YOLO class in CardSegmenter
        with patch("src.core.card_segmenter.YOLO", return_value=mock_yolo):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = segmenter.segment_cards(image)
            self.assertEqual(len(results), 1)
            self.assertIn("mask", results[0])
            self.assertIn("bbox", results[0])
            self.assertEqual(results[0]["mask"].shape, (100, 100))
            self.assertEqual(results[0]["bbox"], [10, 10, 90, 90])

    def test_segment_cards_error_handling(self):
        """Test case for error handling during segmentation.

        This test verifies that the segment_cards method returns an empty list when the
        mocked YOLO model raises an exception during prediction.
        """
        # Mock the YOLO model to raise an exception
        mock_yolo = MagicMock()
        mock_yolo.predict.side_effect = Exception("Segmentation error")


        # Patch the YOLO class in CardSegmenter
        with patch("src.core.card_segmenter.YOLO", return_value=mock_yolo):
            segmenter = CardSegmenter()
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            results = segmenter.segment_cards(image)
            self.assertEqual(results, [])

    def test_segment_cards_with_renaming(self):
        """Test case for saving segmented cards with renamed filenames.

        This test verifies that the segment_cards method correctly saves segmented card
        images with filenames based on the identified card names when saving is enabled
        in the configuration. It also checks that no files are created when saving is
        disabled.
        """
        # Mock YOLO model
        mock_yolo = self._create_mock_yolo()

        # Mock card name identification
        mock_identify_card_name = MagicMock(return_value="Test Card Name")

        # Create a temporary directory for saving images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock ConfigManager to enable saving and set the temporary directory
            mock_config_manager = MagicMock()
            mock_config_manager.get_save_segmented_images.return_value = True
            mock_config_manager.get_save_segmented_images_path.return_value = temp_dir

            with patch("src.core.card_segmenter.YOLO", return_value=mock_yolo), \
                    patch("src.core.card_segmenter.CardSegmenter.identify_card_name", mock_identify_card_name), \
                    patch("src.core.card_segmenter.ConfigManager", return_value=mock_config_manager):

                segmenter = CardSegmenter()
                image = np.zeros((100, 100, 3), dtype=np.uint8)
                segmenter.segment_cards(image)

                # Assert that the image was saved with the correct filename
                expected_filename = os.path.join(temp_dir, "Test_Card_Name.png")
                self.assertTrue(os.path.exists(expected_filename))

        # Test with saving disabled
        mock_config_manager.get_save_segmented_images.return_value = False
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config_manager.get_save_segmented_images_path.return_value = temp_dir
            with patch("src.core.card_segmenter.YOLO", return_value=mock_yolo), \
                    patch("src.core.card_segmenter.CardSegmenter.identify_card_name", mock_identify_card_name), \
                    patch("src.core.card_segmenter.ConfigManager", return_value=mock_config_manager):

                segmenter = CardSegmenter()
                image = np.zeros((100, 100, 3), dtype=np.uint8)
                segmenter.segment_cards(image)

                # Assert that no files were created
                self.assertEqual(len(os.listdir(temp_dir)), 0)

if __name__ == '__main__':
    unittest.main()
