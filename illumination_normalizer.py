import cv2
import numpy as np
from typing import Tuple

def normalize_illumination(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """Normalizes illumination in an image using CLAHE.

    Args:
        image (NumPy array): The input image.
        clip_limit (float): Threshold for contrast limiting.
        tile_grid_size (tuple): Size of grid for histogram equalization.

    Returns:
        NumPy array: The illumination-normalized image.
    """
    lab: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl: np.ndarray = clahe.apply(l)
    limg: np.ndarray = cv2.merge((cl, a, b))
    normalized_image: np.ndarray = cv2.cvtColor(limg, cv2.COLOR_Lab2BGR)
    return normalized_image
