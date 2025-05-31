# Standard library imports
from typing import Tuple # Tuple is not used, can be removed

# Third-party imports
import cv2
import numpy as np

# Module-level logger (optional)
# import logging
# logger = logging.getLogger(__name__)

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Converts a color image to grayscale.

    This function takes an image in BGR (Blue, Green, Red) format, which is the
    default color format for OpenCV, and converts it into a single-channel
    grayscale image.

    Args:
        image (np.ndarray): The input image as a NumPy array.
                            It is assumed to be in BGR color format.

    Returns:
        np.ndarray: The converted grayscale image as a NumPy array.
                    This will be a 2D array if the input was 3D.

    Raises:
        cv2.error: If the input image is not valid or the conversion fails
                   within OpenCV.
    """
    # Check if the image is already grayscale (e.g., has only 2 dimensions)
    if image.ndim == 2:
        # logger.debug("Image is already grayscale. Returning as is.") # Optional logging
        return image
    elif image.ndim == 3 and image.shape[2] == 1: # Grayscale but with a channel dimension
        # logger.debug("Image is grayscale with a channel dimension. Squeezing and returning.") # Optional logging
        return image.squeeze(axis=2) # Remove the singleton dimension

    # logger.debug(f"Converting BGR image of shape {image.shape} to grayscale.") # Optional logging
    # Perform the color space conversion from BGR to GRAY
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # logger.debug(f"Grayscale image created with shape {grayscale_image.shape}.") # Optional logging
    return grayscale_image
