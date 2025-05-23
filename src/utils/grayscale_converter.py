import cv2
import numpy as np
from typing import Tuple

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Converts an image to grayscale.

    This function uses OpenCV's `cvtColor` function to convert a BGR image to grayscale.

    Args:
        image: The input image as a NumPy array.  It is assumed to be in BGR format.

    Returns:
        The grayscale image as a NumPy array.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
