import cv2
import numpy as np
from typing import Tuple

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Converts an image to grayscale.

    Args:
        image (NumPy array): The input image.

    Returns:
        NumPy array: The grayscale image.
    """
    gray_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image
