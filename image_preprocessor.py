from noise_reducer import reduce_noise
from illumination_normalizer import normalize_illumination
from contrast_checker import check_low_contrast
from grayscale_converter import convert_to_grayscale
import numpy as np
from typing import Dict, Any

class ImagePreprocessor:
    """
    Preprocesses images by applying a series of transformations based on a configuration.

    Attributes:
        config (Dict[str, Any]): A dictionary containing the preprocessing configuration.
        steps (Dict[str, Any]): A dictionary mapping preprocessing step names to their corresponding functions.
    """
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the ImagePreprocessor with a configuration.

        Args:
            config (Dict[str, Any]): A dictionary containing the preprocessing configuration.
                                     The configuration should define the steps to be applied and their parameters.
        """
        self.config = config
        self.steps = {
            "noise_reduction": reduce_noise,
            "illumination_normalization": normalize_illumination,
            "grayscale_conversion": convert_to_grayscale,
        }

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Applies the configured preprocessing steps to an image.

        Args:
            image (np.ndarray): The input image as a NumPy array.

        Returns:
            np.ndarray: The preprocessed image as a NumPy array.
        """
        for step_name, params in self.config.get("steps", {}).items():
            if step_name in self.steps:
                if step_name == "noise_reduction":
                    image = self.steps[step_name](image, **params)
                elif step_name == "illumination_normalization":
                    image = self.steps[step_name](image, **params)
                elif step_name == "grayscale_conversion":
                    image = self.steps[step_name](image)
        return image

    def check_contrast(self, image: np.ndarray) -> bool:
        """
        Checks the contrast of an image.

        Args:
            image (np.ndarray): The input image as a NumPy array.

        Returns:
            bool: True if the image has low contrast, False otherwise.
        """
        contrast_config = self.config.get("contrast_check", {})
        threshold = contrast_config.get("threshold", 0.35)
        return check_low_contrast(image, threshold=threshold)
