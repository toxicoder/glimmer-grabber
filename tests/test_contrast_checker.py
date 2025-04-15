import unittest
import cv2
import numpy as np
from src.utils.contrast_checker import check_low_contrast
from typing import Tuple

class TestContrastChecker(unittest.TestCase):
    """Tests for the contrast checking utility."""
    def test_check_low_contrast_low(self) -> None:
        """Test low contrast image.

        This test checks if the function correctly identifies a low contrast image,
        which is created as a uniform gray image.
        """
        image: np.ndarray = np.full((100, 100, 3), 128, dtype=np.uint8)

        self.assertTrue(check_low_contrast(image))

    def test_check_low_contrast_high(self) -> None:
        """Test high contrast image.

        This test checks if the function correctly identifies a high contrast image,
        which is created with distinct black and white regions.
        """
        image: np.ndarray = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:50, :, :] = 255

        self.assertFalse(check_low_contrast(image))

    def test_check_low_contrast_with_threshold(self) -> None:
        """Test contrast check with different thresholds.

        This test verifies the function's behavior with different threshold values.
        It uses a medium contrast image and checks if the function returns the
        expected results with higher and lower thresholds.
        """
        image: np.ndarray = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:50, :, :] = 100
        image[50:, :, :] = 200

        # Check with a higher threshold
        self.assertFalse(check_low_contrast(image, threshold=0.5))
        # Check with a lower threshold
        self.assertFalse(check_low_contrast(image, threshold=0.1))

if __name__ == '__main__':
    unittest.main()
