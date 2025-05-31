import unittest
from unittest.mock import patch, MagicMock # Added MagicMock
import cv2
import numpy as np
from src.core.image_preprocessor import ImagePreprocessor, PreprocessingConfig # Import type alias

class TestImagePreprocessor(unittest.TestCase):
    """Tests for the ImagePreprocessor class."""

    def setUp(self):
        """Set up common test data."""
        self.dummy_image_color = np.zeros((100, 100, 3), dtype=np.uint8)
        self.dummy_image_gray = np.zeros((100, 100), dtype=np.uint8)

        # Default full config for ImagePreprocessor instance creation
        self.default_full_config: PreprocessingConfig = {
            "steps": {
                "noise_reduction": {"strength": 5, "color_strength": 5},
                "illumination_normalization": {"clip_limit": 1.5, "tile_grid_size": (4, 4)},
                "grayscale_conversion": {}, # No params for grayscale
            },
            "contrast_check": {"threshold": 0.35},
        }
        self.preprocessor_full_config = ImagePreprocessor(self.default_full_config)

    def test_init_stores_config(self):
        """Test that the constructor correctly stores the configuration."""
        self.assertEqual(self.preprocessor_full_config.config, self.default_full_config)

    @patch('src.core.image_preprocessor.reduce_noise')
    @patch('src.core.image_preprocessor.normalize_illumination')
    @patch('src.core.image_preprocessor.convert_to_grayscale')
    def test_preprocess_all_steps_called(self, mock_to_gray, mock_norm_illum, mock_reduce_noise):
        """Test that preprocess calls all configured steps with correct parameters."""
        # Make mocks return a modified image to ensure the pipeline flows
        mock_reduce_noise.return_value = np.ones_like(self.dummy_image_color)
        mock_norm_illum.return_value = np.full_like(self.dummy_image_color, 2)
        mock_to_gray.return_value = np.full_like(self.dummy_image_gray, 3) # Grayscale output

        processed_image = self.preprocessor_full_config.preprocess(self.dummy_image_color)

        mock_reduce_noise.assert_called_once_with(
            unittest.mock.ANY, # The image passed to it
            strength=self.default_full_config["steps"]["noise_reduction"]["strength"],
            color_strength=self.default_full_config["steps"]["noise_reduction"]["color_strength"]
        )
        # The image passed to normalize_illumination should be the result of reduce_noise
        np.testing.assert_array_equal(mock_norm_illum.call_args[0][0], mock_reduce_noise.return_value)
        mock_norm_illum.assert_called_once_with(
            unittest.mock.ANY,
            clip_limit=self.default_full_config["steps"]["illumination_normalization"]["clip_limit"],
            tile_grid_size=self.default_full_config["steps"]["illumination_normalization"]["tile_grid_size"]
        )
        # The image passed to convert_to_grayscale should be the result of normalize_illumination
        np.testing.assert_array_equal(mock_to_gray.call_args[0][0], mock_norm_illum.return_value)
        mock_to_gray.assert_called_once_with(unittest.mock.ANY)

        # Check final output is from the last step
        np.testing.assert_array_equal(processed_image, mock_to_gray.return_value)
        self.assertEqual(len(processed_image.shape), 2) # Should be grayscale

    @patch('src.core.image_preprocessor.reduce_noise')
    @patch('src.core.image_preprocessor.normalize_illumination')
    def test_preprocess_subset_of_steps(self, mock_norm_illum, mock_reduce_noise):
        """Test preprocessing with only a subset of steps, ensuring correct output type."""
        config_subset: PreprocessingConfig = {
            "steps": {
                "noise_reduction": {"strength": 10}, # Only strength, color_strength uses util default
                "illumination_normalization": {"clip_limit": 2.0}, # tile_grid_size uses util default
            }
            # No grayscale_conversion step
        }
        preprocessor_subset = ImagePreprocessor(config_subset)

        mock_reduce_noise.return_value = self.dummy_image_color # Assume it returns color
        mock_norm_illum.return_value = self.dummy_image_color # Assume it returns color

        processed_image = preprocessor_subset.preprocess(self.dummy_image_color)

        mock_reduce_noise.assert_called_once_with(unittest.mock.ANY, strength=10)
        mock_norm_illum.assert_called_once_with(unittest.mock.ANY, clip_limit=2.0)
        self.assertEqual(len(processed_image.shape), 3) # Should remain color

    def test_preprocess_no_steps_configured(self):
        """Test preprocessing when no steps are defined in the config."""
        config_no_steps: PreprocessingConfig = {"steps": {}}
        preprocessor_no_steps = ImagePreprocessor(config_no_steps)

        # preprocess should return a copy of the original image
        processed_image = preprocessor_no_steps.preprocess(self.dummy_image_color)
        np.testing.assert_array_equal(processed_image, self.dummy_image_color)
        self.assertIsNot(processed_image, self.dummy_image_color) # Ensure it's a copy

    def test_preprocess_unknown_step_configured(self):
        """Test that an unknown step in config is skipped with a warning (logged)."""
        config_unknown_step: PreprocessingConfig = {
            "steps": {"unknown_fancy_filter": {"param": 1}}
        }
        preprocessor_unknown = ImagePreprocessor(config_unknown_step)

        # Expect a log warning, but the method should complete and return a copy.
        with self.assertLogs(logger='src.core.image_preprocessor', level='WARNING') as log_cm:
            processed_image = preprocessor_unknown.preprocess(self.dummy_image_color)

        self.assertTrue(any("Unknown preprocessing step configured: 'unknown_fancy_filter'" in msg for msg in log_cm.output))
        np.testing.assert_array_equal(processed_image, self.dummy_image_color)


    @patch('src.core.image_preprocessor.check_low_contrast')
    def test_check_contrast_uses_config_threshold(self, mock_util_check_low_contrast):
        """Test check_contrast uses the threshold from its configuration."""
        config_custom_thresh: PreprocessingConfig = {
            "contrast_check": {"threshold": 0.55}
        }
        preprocessor_custom = ImagePreprocessor(config_custom_thresh)

        mock_util_check_low_contrast.return_value = True # Dummy return

        result = preprocessor_custom.check_contrast(self.dummy_image_gray)

        self.assertTrue(result)
        mock_util_check_low_contrast.assert_called_once_with(self.dummy_image_gray, threshold=0.55)

    @patch('src.core.image_preprocessor.check_low_contrast')
    def test_check_contrast_uses_default_threshold_if_not_in_config(self, mock_util_check_low_contrast):
        """Test check_contrast uses its default threshold if not specified in config."""
        config_no_thresh: PreprocessingConfig = {"contrast_check": {}} # Empty contrast_check dict
        preprocessor_no_thresh = ImagePreprocessor(config_no_thresh)

        mock_util_check_low_contrast.return_value = False

        result = preprocessor_no_thresh.check_contrast(self.dummy_image_gray)

        self.assertFalse(result)
        # The default threshold in ImagePreprocessor.check_contrast is 0.35
        mock_util_check_low_contrast.assert_called_once_with(self.dummy_image_gray, threshold=0.35)

    def test_check_contrast_actual_logic(self):
        """Test the contrast checking functionality with actual images."""
        # Low contrast image: all pixels are gray
        low_contrast_image = np.full((100, 100, 3), 128, dtype=np.uint8)
        # High contrast image: half black, half white
        high_contrast_image = np.zeros((100, 100, 3), dtype=np.uint8)
        high_contrast_image[:50, :, :] = 255 # Top half white

        # Default config for ImagePreprocessor uses threshold 0.35 for contrast_check
        preprocessor = ImagePreprocessor(self.default_full_config)

        self.assertTrue(preprocessor.check_contrast(low_contrast_image))
        self.assertFalse(preprocessor.check_contrast(high_contrast_image))

        # Test with a different threshold via config
        custom_config = {"contrast_check": {"threshold": 0.01}} # Very strict, most things are not low contrast
        preprocessor_custom = ImagePreprocessor(custom_config)
        # Even the 'low_contrast_image' might pass this strict threshold if it's not perfectly flat
        # For a perfectly flat image, is_low_contrast will be True if (p_upper - p_lower) is 0.
        # The skimage default fraction_threshold for is_low_contrast is 0.05,
        # so it checks the range of the central 90% of pixels. If that range is 0, it's low contrast.
        self.assertTrue(preprocessor_custom.check_contrast(low_contrast_image)) # Still low contrast (range is 0)
        self.assertFalse(preprocessor_custom.check_contrast(high_contrast_image))


if __name__ == '__main__':
    unittest.main()
