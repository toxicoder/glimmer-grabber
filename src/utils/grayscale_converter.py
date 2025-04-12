import cv2
import numpy as np
from typing import Tuple

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Converts an image to grayscale.

    Args:
        image (np.ndarray): The input image as a NumPy array.

    Returns:
        np.ndarray: The grayscale image as a NumPy array.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
