import numpy as np
from PIL import Image
import io

def process_image(image_bytes: bytes) -> dict:
    """
    Processes an image to extract features.
    Accepts image bytes and returns a dictionary of features.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        # Placeholder for actual image processing logic
        return {"width": image_np.shape[1], "height": image_np.shape[0]}
    except Exception as e:
        # In a real scenario, you'd want more robust error handling
        print(f"Error processing image: {e}")
        return {}
