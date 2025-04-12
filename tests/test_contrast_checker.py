import unittest
import cv2
import numpy as np
from src.utils.contrast_checker import check_low_contrast

class TestContrastChecker(unittest.TestCase):
    def test_check_low_contrast_low(self):
        # Create a low contrast image (uniform gray)
        image = np.full((100, 100, 3), 128, dtype=np.uint8)

        self.assertTrue(check_low_contrast(image))

    def test_check_low_contrast_high(self):
        # Create a high contrast image (black and white)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:50, :, :] = 255

        self.assertFalse(check_low_contrast(image))

    def test_check_low_contrast_with_threshold(self):
        # Create a medium contrast image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:50, :, :] = 100
        image[50:, :, :] = 200

        # Check with a higher threshold
        self.assertFalse(check_low_contrast(image, threshold=0.5))
        # Check with a lower threshold
        self.assertTrue(check_low_contrast(image, threshold=0.1))

if __name__ == '__main__':
    unittest.main()
