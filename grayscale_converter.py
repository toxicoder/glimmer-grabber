import cv2

def convert_to_grayscale(image):
    """Converts an image to grayscale.

    Args:
        image (NumPy array): The input image.

    Returns:
        NumPy array: The grayscale image.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image
