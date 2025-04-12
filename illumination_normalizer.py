import cv2

def normalize_illumination(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Normalizes illumination in an image using CLAHE.

    Args:
        image (NumPy array): The input image.
        clip_limit (float): Threshold for contrast limiting.
        tile_grid_size (tuple): Size of grid for histogram equalization.

    Returns:
        NumPy array: The illumination-normalized image.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    normalized_image = cv2.cvtColor(limg, cv2.COLOR_Lab2BGR)
    return normalized_image
