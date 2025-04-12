from skimage.exposure import is_low_contrast
import cv2
import numpy as np
from typing import Tuple

def check_low_contrast(image: np.ndarray, threshold: float = 0.35) -> bool:
    """Checks if an image has low contrast.

    Args:
        image (NumPy array): The input image.
        threshold (float):  Threshold value to consider an image as low contrast.

    Returns:
        bool: True if the image has low contrast, False otherwise.
    """
    gray_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return is_low_contrast(gray_image, fraction_threshold=threshold)
