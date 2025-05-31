# Standard library imports
import logging
from typing import Any, Dict, Callable # Callable for step functions

# Third-party imports
import numpy as np

# Application-specific imports from src.utils
from src.utils.noise_reducer import reduce_noise
from src.utils.illumination_normalizer import normalize_illumination
from src.utils.contrast_checker import check_low_contrast
from src.utils.grayscale_converter import convert_to_grayscale

# Module-level logger
logger = logging.getLogger(__name__)

# Type alias for the preprocessing configuration structure
PreprocessingConfig = Dict[str, Dict[str, Any]] # e.g., {"steps": {"noise_reduction": {"strength": 10}}}

class ImagePreprocessor:
    """
    Applies a series of configured image preprocessing transformations.

    This class orchestrates various image preprocessing steps, such as noise reduction,
    illumination normalization, and grayscale conversion. The specific steps and
    their parameters are determined by a configuration dictionary provided during
    initialization. This allows for flexible and configurable image preprocessing pipelines.

    Attributes:
        config (PreprocessingConfig): The configuration dictionary specifying which
                                      preprocessing steps to apply and their parameters.
                                      Example: `{"steps": {"noise_reduction": {"strength": 5}}}`
        _step_functions (Dict[str, Callable]): A private mapping of step names (keys from config)
                                             to their corresponding callable functions from `src.utils`.
    """
    def __init__(self, config: PreprocessingConfig) -> None:
        """
        Initializes the ImagePreprocessor with a given preprocessing configuration.

        Args:
            config (PreprocessingConfig): A dictionary that defines the preprocessing
                                          pipeline. It should ideally contain a "steps" key,
                                          which is a dictionary where keys are step names
                                          (e.g., "noise_reduction") and values are dictionaries
                                          of parameters for that step.
                                          It can also contain a "contrast_check" key for
                                          contrast checking parameters.
        """
        self.config: PreprocessingConfig = config
        logger.debug(f"ImagePreprocessor initialized with configuration: {self.config}")

        # Mapping of step names (as used in config keys) to actual function calls
        self._step_functions: Dict[str, Callable] = {
            "noise_reduction": reduce_noise,
            "illumination_normalization": normalize_illumination,
            "grayscale_conversion": convert_to_grayscale,
            # Add other preprocessing functions here as they are developed
            # e.g., "deskew_image": deskew_function,
        }

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Applies the configured sequence of preprocessing steps to an input image.

        The steps are applied in the order they are defined under the "steps"
        key in the configuration dictionary. If a step defined in the config
        is not recognized (i.e., not in `self._step_functions`), it will be skipped
        with a warning.

        Args:
            image (np.ndarray): The input image as a NumPy array.

        Returns:
            np.ndarray: The preprocessed image as a NumPy array.

        Note:
            The method operates on a copy of the image, leaving the original unchanged.
        """
        # Create a copy of the image to avoid modifying the original array in place
        processed_image = image.copy()

        # Retrieve the dictionary of steps from the configuration.
        # Defaults to an empty dictionary if "steps" key is not found.
        steps_to_apply: Dict[str, Dict[str, Any]] = self.config.get("steps", {})
        logger.info(f"Starting image preprocessing with configured steps: {list(steps_to_apply.keys())}")

        # Iterate through each configured step and its parameters
        for step_name, params in steps_to_apply.items():
            # Check if the step_name is a recognized preprocessing function
            if step_name in self._step_functions:
                step_function = self._step_functions[step_name]
                try:
                    logger.debug(f"Applying preprocessing step: '{step_name}' with parameters: {params}")
                    # Call the appropriate utility function.
                    # Grayscale conversion is a special case that typically doesn't take extra parameters.
                    if step_name == "grayscale_conversion":
                        processed_image = step_function(processed_image)
                    else:
                        # For other functions, unpack parameters from the config dictionary
                        processed_image = step_function(processed_image, **params)
                    logger.debug(f"Step '{step_name}' applied successfully.")
                except Exception as e:
                    # Log an error if any step fails
                    logger.error(f"Error applying preprocessing step '{step_name}': {e}", exc_info=True)
                    # Depending on desired robustness:
                    # - Could re-raise the exception: `raise`
                    # - Could return the original image or current state: `return image` or `return processed_image`
                    # - For now, it continues with the image as it was before this failed step,
                    #   allowing subsequent steps to proceed if possible.
            else:
                # Log a warning if a configured step is not recognized
                logger.warning(f"Unknown preprocessing step configured: '{step_name}'. Skipping this step.")

        logger.info("Image preprocessing pipeline completed.")
        return processed_image

    def check_contrast(self, image: np.ndarray) -> bool:
        """
        Checks if the input image has low contrast based on configured parameters.

        This method uses the `check_low_contrast` utility function from `src.utils`.
        The threshold for determining low contrast is sourced from the "contrast_check"
        section of the `self.config` dictionary. If not specified, a default
        threshold is used.

        Args:
            image (np.ndarray): The input image as a NumPy array to check for contrast.

        Returns:
            bool: True if the image is determined to have low contrast, False otherwise.
        """
        # Retrieve the configuration for contrast checking.
        # Defaults to an empty dictionary if "contrast_check" is not in config.
        contrast_config: Dict[str, Any] = self.config.get("contrast_check", {})
        # Get the threshold from config, with a default value (e.g., 0.35) if not specified.
        # This default should match the one in `utils.contrast_checker` or be configurable.
        threshold: float = contrast_config.get("threshold", 0.35)

        logger.debug(f"Checking image contrast with threshold: {threshold}")
        # Call the utility function to perform the contrast check
        is_low = check_low_contrast(image, threshold=threshold)
        logger.info(f"Image contrast check result: {'Low contrast' if is_low else 'Sufficient contrast'}.")
        return is_low
