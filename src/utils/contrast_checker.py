from skimage.exposure import is_low_contrast
import cv2
import numpy as np
from typing import Tuple

def check_low_contrast(image: np.ndarray, threshold: float = 0.35) -> bool:
    """Checks if an image has low contrast.

    This function converts the input image to grayscale and then uses the `is_low_contrast`
    function from `skimage.exposure` to determine if the image has low contrast.

    Args:
        image: The input image as a NumPy array.
        threshold: The threshold value to consider an image as low contrast (default: 0.35).
            This value represents the fraction of pixels that are allowed to span the
            full intensity range.

    Returns:
        True if the image has low contrast, False otherwise.
    """
    gray_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return bool(is_low_contrast(gray_image, fraction_threshold=threshold))
