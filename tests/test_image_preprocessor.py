import unittest
import cv2
import numpy as np
from src.core.image_preprocessor import ImagePreprocessor

class TestImagePreprocessor(unittest.TestCase):
    """Tests for the ImagePreprocessor class."""
    def test_preprocess_with_all_steps(self):
        """Test preprocessing with all steps enabled.

        This test checks if the ImagePreprocessor correctly applies all configured
        preprocessing steps (noise reduction, illumination normalization, and grayscale
        conversion) to an image. It verifies that the output image is grayscale (2D)
        after preprocessing.
        """
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
        """Test preprocessing with a subset of steps enabled.

        This test checks if the ImagePreprocessor correctly applies a subset of the
        configured preprocessing steps (noise reduction and illumination normalization)
        to an image. It verifies that the output image remains in color (3D) after
        preprocessing, as grayscale conversion is not included.
        """
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
        """Test the contrast checking functionality.

        This test checks if the ImagePreprocessor correctly assesses the contrast of
        images. It uses a low contrast image and a high contrast image, and verifies
        that the check_contrast method returns True for the low contrast image and
        False for the high contrast image, based on the configured threshold.
        """
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
