import cv2
import numpy as np
from typing import Tuple

def reduce_noise(image: np.ndarray, strength: float = 10.0, color_strength: float = 10.0, template_window_size: int = 7, search_window_size: int = 21) -> np.ndarray:
    """Reduces noise in a color image using fast Non-local Means Denoising for color images.

    This function uses cv2.fastNlMeansDenoisingColored, which is optimized for speed
    compared to the more general cv2.fastNlMeansDenoising.

    Args:
        image: The input color image as a NumPy array.
        strength: Strength of the denoising filter (for luminance). Higher values mean stronger denoising (default: 10.0).
        color_strength: Strength of the color denoising filter. A higher value results in stronger color denoising (default: 10.0).
        template_window_size: Size of the template patch that is used to compute weights. Should be odd (default: 7).
        search_window_size: Size of the search window that is used to compute a weighted average for the given pixel. Should be odd (default: 21).

    Returns:
        The denoised image as a NumPy array.
    """
+    # Ensure parameters are integers
+    strength = int(strength)
+    color_strength = int(color_strength)
    denoised_image: np.ndarray = cv2.fastNlMeansDenoisingColored(
        image,
        None,

        strength,
        color_strength,
        template_window_size,
        search_window_size,
    )
    return denoised_image
