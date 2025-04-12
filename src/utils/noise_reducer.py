import cv2
import numpy as np
from typing import Tuple

def reduce_noise(image: np.ndarray, strength: float = 10.0, color_strength: float = 10.0, template_window_size: int = 7, search_window_size: int = 21) -> np.ndarray:
    """Reduces noise in a color image using cv2.fastNlMeansDenoisingColored.

    Args:
        image (NumPy array): The input color image.
        strength (int): Strength of the denoising filter. Higher values mean stronger denoising.
        color_strength (int): Strength of the color denoising. Higher values mean stronger color denoising.
        template_window_size (int): Size of the template patch that is used to compute weights. Should be odd.
        search_window_size (int): Size of the search window that is used to compute weighted average for the given pixel. Should be odd.

    Returns:
        NumPy array: The denoised image.
    """
+    # Ensure parameters are integers
+    strength = int(strength)
+    color_strength = int(color_strength)
    denoised_image: np.ndarray = cv2.fastNlMeansDenoisingColored(
        image,
        None,

         template_window_size,
         search_window_size,
     )
-    return denoised_image
+    return denoised_image
