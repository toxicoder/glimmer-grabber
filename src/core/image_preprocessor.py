from src.utils.noise_reducer import reduce_noise
from src.utils.illumination_normalizer import normalize_illumination
from src.utils.contrast_checker import check_low_contrast
from src.utils.grayscale_converter import convert_to_grayscale
import numpy as np
from typing import Dict, Any

PreprocessingConfig = Dict[str, Dict[str, Any]]

class ImagePreprocessor:
    """Preprocesses images by applying a series of transformations based on a configuration.

    Attributes:
        config: A dictionary containing the preprocessing configuration.
        steps: A dictionary mapping preprocessing step names to their corresponding functions.
    """
    def __init__(self, config: PreprocessingConfig) -> None:
        """Initializes the ImagePreprocessor with a configuration.

        Args:
            config: A dictionary containing the preprocessing configuration.
                The configuration should define the steps to be applied and their parameters.
        """
        self.config: PreprocessingConfig = config
        self.steps = {
            "noise_reduction": reduce_noise,
            "illumination_normalization": normalize_illumination,
            "grayscale_conversion": convert_to_grayscale,
        }

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Applies the configured preprocessing steps to an image.

        Args:
            image: The input image as a NumPy array.

        Returns:
            The preprocessed image as a NumPy array.
        """
        steps: Dict[str, Dict[str, Any]] = self.config.get("steps", {})
        for step_name, params in steps.items():
            if step_name in self.steps:
                if step_name == "noise_reduction":
                    image = self.steps[step_name](image, **params)
                elif step_name == "illumination_normalization":
                    image = self.steps[step_name](image, **params)
                elif step_name == "grayscale_conversion":
                    image = self.steps[step_name](image)
        return image

    def check_contrast(self, image: np.ndarray) -> bool:
        """Checks the contrast of an image.

        Args:
            image: The input image as a NumPy array.

        Returns:
            True if the image has low contrast, False otherwise.
        """
        contrast_config: Dict[str, Any] = self.config.get("contrast_check", {})
        threshold: float = contrast_config.get("threshold", 0.35)
        return check_low_contrast(image, threshold=threshold)
