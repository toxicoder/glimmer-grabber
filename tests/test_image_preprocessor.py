import unittest
import cv2
import numpy as np
from image_preprocessor import ImagePreprocessor

class TestImagePreprocessor(unittest.TestCase):
    def test_preprocess_with_all_steps(self):
        # Create a dummy image
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Define a configuration with all preprocessing steps
        config = {
            "steps": {
                "noise_reduction": {"strength": 5, "color_strength": 5},
                "illumination_normalization": {"clip_limit": 1.5, "tile_grid_size": (4, 4)},
                "grayscale_conversion": {},
            },
            "contrast_check": {"threshold": 0.4},
        }

        # Create an ImagePreprocessor instance
        preprocessor = ImagePreprocessor(config)

        # Preprocess the image
        processed_image = preprocessor.preprocess(image)

        # Check if the output image is grayscale (2D)
        self.assertEqual(len(processed_image.shape), 2)

    def test_preprocess_with_some_steps(self):
        # Create a dummy image
        image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Define a configuration with only noise reduction and illumination normalization
        config = {
            "steps": {
                "noise_reduction": {"strength": 10, "color_strength": 10},
                "illumination_normalization": {"clip_limit": 2.0, "tile_grid_size": (8, 8)},
            },
            "contrast_check": {"threshold": 0.3},
        }

        # Create an ImagePreprocessor instance
        preprocessor = ImagePreprocessor(config)

        # Preprocess the image
        processed_image = preprocessor.preprocess(image)

        # Check if the output image is still color (3D)
        self.assertEqual(len(processed_image.shape), 3)

    def test_check_contrast(self):
        # Create a dummy low contrast image
        low_contrast_image = np.full((100, 100, 3), 128, dtype=np.uint8)

        # Create a dummy high contrast image
        high_contrast_image = np.zeros((100, 100, 3), dtype=np.uint8)
        high_contrast_image[:50, :, :] = 255

        # Define a configuration with a contrast threshold
        config = {"contrast_check": {"threshold": 0.35}}

        # Create an ImagePreprocessor instance
        preprocessor = ImagePreprocessor(config)

        # Check contrast of the low contrast image
        self.assertTrue(preprocessor.check_contrast(low_contrast_image))

        # Check contrast of the high contrast image
        self.assertFalse(preprocessor.check_contrast(high_contrast_image))

if __name__ == '__main__':
    unittest.main()
