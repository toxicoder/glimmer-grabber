import os
import requests

LORCANA_API_URL = os.environ.get("LORCANA_API_URL")

def get_card_details(card_name: str) -> dict:
    """
    Calls the Lorcana API to get details for a specific card.
    """
    try:
        response = requests.get(f"{LORCANA_API_URL}/cards/{card_name}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Lorcana API: {e}")
        return {}

def extract_data(card_texts: list[str]) -> list[dict]:
    """
    Extracts relevant information from processed data.
    """
    card_details = []
    for card_text in card_texts:
        # This is a simplification. In a real application, you would need to
        # parse the OCR text to identify the card name.
        card_name = card_text.strip()
        if card_name:
            details = get_card_details(card_name)
            if details:
                card_details.append(details)
    return card_details
