# Standard library imports
from typing import Tuple # Tuple is not used, can be removed

# Third-party imports
import cv2
import numpy as np

# Module-level logger (optional)
# import logging
# logger = logging.getLogger(__name__)

def reduce_noise(
    image: np.ndarray,
    strength: int = 10,
    color_strength: int = 10,
    template_window_size: int = 7,
    search_window_size: int = 21
) -> np.ndarray:
    """
    Reduces noise in a color image using the fast Non-Local Means Denoising algorithm.

    This function applies `cv2.fastNlMeansDenoisingColored`, which is specifically
    designed for denoising color images. It considers similarity between patches
    in a larger search window to average out noise, preserving edges better than
    simpler blurring techniques.

    Args:
        image (np.ndarray): The input color image as a NumPy array (BGR format).
        strength (int): Parameter regulating filter strength for luminance component.
                        Higher values remove more noise but may blur details.
                        Defaults to 10.
        color_strength (int): Parameter regulating filter strength for color components.
                              Same as `strength` but for color. Defaults to 10.
        template_window_size (int): Size (in pixels) of the template patch used to
                                    compute weights. Should be an odd number.
                                    Defaults to 7. (e.g., 7x7 patch)
        search_window_size (int): Size (in pixels) of the window in which to search for
                                  similar patches. Should be an odd number.
                                  A larger search window increases processing time.
                                  Defaults to 21. (e.g., 21x21 window)

    Returns:
        np.ndarray: The denoised image as a NumPy array in BGR format.

    Raises:
        cv2.error: If any OpenCV operations fail during the denoising process.
    """
    # logger.debug(f"Reducing noise with strength={strength}, color_strength={color_strength}, " # Optional logging
    #              f"template_window_size={template_window_size}, search_window_size={search_window_size}")

    # Apply the Non-Local Means Denoising algorithm for colored images.
    # The `None` argument for `dst` means OpenCV will create the destination image.
    # `h` (strength) controls luminance denoising.
    # `hColor` (color_strength) controls color denoising.
    denoised_image: np.ndarray = cv2.fastNlMeansDenoisingColored(
        src=image,
        dst=None, # Output array; None means it's created by the function
        h=float(strength), # Filter strength for luminance component
        hColor=float(color_strength), # Filter strength for color components
        templateWindowSize=template_window_size,
        searchWindowSize=search_window_size,
    )

    # logger.debug("Noise reduction complete.") # Optional logging
    return denoised_image
