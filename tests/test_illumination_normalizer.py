import unittest
import cv2
import numpy as np
from src.utils.illumination_normalizer import normalize_illumination
from typing import Tuple

class TestIlluminationNormalizer(unittest.TestCase):
    def test_normalize_illumination(self) -> None:
        # Create a dummy image with some illumination variation
        image: np.ndarray = np.zeros((100, 100, 3), dtype=np.uint8)
        gradient: np.ndarray = np.linspace(0, 255, 100, dtype=np.uint8)
        image[:, :, 0] = gradient
        image[:, :, 1] = gradient
        image[:, :, 2] = gradient

        # Apply illumination normalization
        normalized_image: np.ndarray = normalize_illumination(image)

        # Check if the output image has the same dimensions as the input
        self.assertEqual(normalized_image.shape, image.shape)
        self.assertEqual(normalized_image.dtype, image.dtype)

if __name__ == '__main__':
    unittest.main()
