import cv2
import numpy as np
from typing import Tuple

def normalize_illumination(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Normalizes illumination in an image using Contrast Limited Adaptive Histogram Equalization (CLAHE).

    Args:
        image (np.ndarray): The input image as a NumPy array.
        clip_limit (float): Threshold for contrast limiting (default: 2.0).
        tile_grid_size (Tuple[int, int]): Size of the grid for histogram equalization (default: (8, 8)).

    Returns:
        np.ndarray: The illumination-normalized image as a NumPy array.
    """
    lab: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl: np.ndarray = clahe.apply(l)
    limg: np.ndarray = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_Lab2BGR)
