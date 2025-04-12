import unittest
import cv2
import numpy as np
from grayscale_converter import convert_to_grayscale

class TestGrayscaleConverter(unittest.TestCase):
    def test_convert_to_grayscale(self):
        # Create a dummy color image
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[:, :, 0] = 255  # Blue channel
        image[:, :, 1] = 128  # Green channel
        image[:, :, 2] = 64   # Red channel

        # Convert to grayscale
        gray_image = convert_to_grayscale(image)

        # Check if the output image is 2D (grayscale)
        self.assertEqual(len(gray_image.shape), 2)
        self.assertEqual(gray_image.shape, (100, 100))
        self.assertEqual(gray_image.dtype, np.uint8)

        # Check if the conversion is correct by comparing with OpenCV's grayscale conversion
        expected_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.assertTrue(np.array_equal(gray_image, expected_gray))

if __name__ == '__main__':
    unittest.main()
