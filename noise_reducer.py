import cv2

def reduce_noise(image, strength=10, color_strength=10, template_window_size=7, search_window_size=21):
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
    denoised_image = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        strength,
        color_strength,
        template_window_size,
        search_window_size,
    )
    return denoised_image
