# Standard library imports
from typing import Tuple # Tuple is not used, can be removed if not planned for future use

# Third-party imports
import cv2
import numpy as np
from skimage.exposure import is_low_contrast # For checking image contrast

# Module-level logger (optional, can be added if logging is needed within this utility)
# import logging
# logger = logging.getLogger(__name__)

def check_low_contrast(image: np.ndarray, threshold: float = 0.35) -> bool:
    """
    Checks if an image has low contrast.

    This function first converts the input image (assumed to be BGR) to grayscale.
    Then, it utilizes the `is_low_contrast` function from the `skimage.exposure`
    module to determine if the contrast is below a specified threshold.

    The `threshold` parameter in this function is passed as the `fraction_threshold`
    argument to `skimage.exposure.is_low_contrast`. In `skimage`, `fraction_threshold`
    determines the proportion of pixels to ignore at both the darkest and brightest
    ends of the intensity histogram when evaluating contrast. The contrast of the
    remaining central portion of pixels is then assessed against an internal default
    (usually 0.1 or 0.05 of the total dynamic range).

    Args:
        image (np.ndarray): The input image as a NumPy array (BGR format).
        threshold (float): The fraction of pixels at the darkest and brightest ends of
                           the histogram to ignore. For example, a value of 0.05 means
                           the top 5% and bottom 5% of pixel intensities are ignored.
                           The contrast is then evaluated on the central 90% of pixels.
                           The default value of 0.35 is quite high, meaning it ignores
                           a large portion of pixels (top/bottom 35%), evaluating contrast
                           on the central 30%. This makes the check sensitive to low
                           contrast in that specific central range.

    Returns:
        bool: True if the image is determined to have low contrast based on the
              evaluation of the central pixel intensities (after ignoring `threshold`
              fraction from both ends), False otherwise.
    """
    # Convert the BGR image to grayscale as contrast is typically assessed on intensity values.
    gray_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use skimage's is_low_contrast function.
    # The `threshold` argument of this function is passed as `fraction_threshold` to skimage.
    # This means `threshold` % of pixels from the darkest end and `threshold` % from the brightest end are ignored.
    # The remaining central (1 - 2*threshold)% of pixels are then evaluated.
    # If their intensity range is less than skimage's internal low-contrast threshold (often 0.1 or 0.05 of total dynamic range),
    # it's considered low contrast.
    is_low = is_low_contrast(gray_image, fraction_threshold=threshold)
    # Example: if threshold = 0.05, central 90% of pixels are considered.
    # Example: if threshold = 0.35 (default), central 30% of pixels are considered.

    # logger.debug(f"Image contrast check: low_contrast={is_low} with fraction_threshold={threshold}") # Optional logging
    return bool(is_low)
