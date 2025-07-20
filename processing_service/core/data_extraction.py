from .card_data_fetcher import CardDataFetcher

import re

def extract_data(card_texts: list[str]) -> list[dict]:
    """
    Extracts card names from OCR text and fetches their details.
    """
    card_fetcher = CardDataFetcher()
    card_details = []
    for card_text in card_texts:
        # Use regex to find potential card names (e.g., all-caps words)
        potential_names = re.findall(r'\b[A-Z\s]+\b', card_text)
        for name in potential_names:
            card_name = name.strip()
            if card_name:
                details = card_fetcher.get_card_details(card_name)
                if details:
                    card_details.append(details)
                    # Assuming the first match is the correct one
                    break
    return card_details
