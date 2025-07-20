import cv2
import numpy as np
import pytesseract
from PIL import Image
import io

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocesses the image for OCR.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    return denoised

def segment_cards(image: np.ndarray) -> list[np.ndarray]:
    """
    Segments the image to find individual cards using Canny edge detection.
    """
    # Canny edge detection
    edges = cv2.Canny(image, 100, 200)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on area and aspect ratio
    card_images = []
    for contour in contours:
        # Approximate the contour to a polygon
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

        # Check if the contour is a rectangle
        if len(approx) == 4:
            # Get the bounding box of the contour
            x, y, w, h = cv2.boundingRect(approx)

            # Filter based on aspect ratio and area to identify cards
            aspect_ratio = w / float(h)
            area = cv2.contourArea(contour)
            if 0.5 < aspect_ratio < 1.5 and area > 1000:
                # Crop the card from the original image
                card_image = image[y : y + h, x : x + w]
                card_images.append(card_image)

    return card_images

def ocr_card(card_image: np.ndarray) -> str:
    """
    Performs OCR on a card image to extract text.
    """
    text = pytesseract.image_to_string(card_image)
    return text

def process_image(image_bytes: bytes) -> list[str]:
    """
    Processes an image to extract features.
    Accepts image bytes and returns a dictionary of features.
    """
    preprocessed_image = preprocess_image(image_bytes)
    card_images = segment_cards(preprocessed_image)

    card_texts = []
    for card_image in card_images:
        text = ocr_card(card_image)
        card_texts.append(text)

    return card_texts
