# Standard library imports
from typing import Tuple # Used for type hinting tile_grid_size

# Third-party imports
import cv2
import numpy as np

# Module-level logger (optional)
# import logging
# logger = logging.getLogger(__name__)

def normalize_illumination(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8)
) -> np.ndarray:
    """
    Normalizes illumination in a color image using CLAHE on the L-channel of LAB color space.

    Contrast Limited Adaptive Histogram Equalization (CLAHE) is applied to the
    Luminosity (L) channel of the image in the LAB color space. This helps to
    improve local contrast and normalize illumination variations across the image
    without significantly affecting color information.

    Args:
        image (np.ndarray): The input image as a NumPy array (assumed to be BGR).
        clip_limit (float): Threshold for contrast limiting in CLAHE. Higher values
                            increase contrast more. Defaults to 2.0.
        tile_grid_size (Tuple[int, int]): Size of the grid for histogram equalization.
                                           Defines the local regions for applying CLAHE.
                                           Defaults to (8, 8).

    Returns:
        np.ndarray: The illumination-normalized image as a NumPy array in BGR format.

    Raises:
        cv2.error: If any OpenCV operations fail (e.g., color conversion, CLAHE application).
    """
    # logger.debug(f"Normalizing illumination with clip_limit={clip_limit}, tile_grid_size={tile_grid_size}") # Optional logging

    # Convert the BGR image to LAB color space.
    # The LAB color space separates luminosity (L) from color information (A and B channels).
    lab_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)

    # Split the LAB image into its L, A, and B channels.
    l_channel, a_channel, b_channel = cv2.split(lab_image)

    # Create a CLAHE object with the specified clip limit and tile grid size.
    # CLAHE is an adaptive version of histogram equalization that works on small regions (tiles)
    # of the image, rather than the entire image, to improve local contrast.
    # `clipLimit` limits the amplification of contrast to avoid over-amplifying noise.
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    # Apply CLAHE to the L (luminosity) channel.
    cl_l_channel: np.ndarray = clahe.apply(l_channel)

    # Merge the CLAHE-enhanced L channel back with the original A and B color channels.
    merged_lab_image: np.ndarray = cv2.merge((cl_l_channel, a_channel, b_channel))

    # Convert the LAB image back to BGR color space.
    normalized_bgr_image: np.ndarray = cv2.cvtColor(merged_lab_image, cv2.COLOR_Lab2BGR)

    # logger.debug("Illumination normalization complete.") # Optional logging
    return normalized_bgr_image
