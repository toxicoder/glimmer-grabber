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
    Segments the image to find individual cards.
    """
    # Placeholder for card segmentation logic
    # In a real application, you would use contour detection or other methods
    return [image]

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
