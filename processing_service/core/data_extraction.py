from .card_data_fetcher import CardDataFetcher

def extract_data(card_texts: list[str]) -> list[dict]:
    """
    Extracts relevant information from processed data.
    """
    card_fetcher = CardDataFetcher()
    card_details = []
    for card_text in card_texts:
        # This is a simplification. In a real application, you would need to
        # parse the OCR text to identify the card name.
        card_name = card_text.strip()
        if card_name:
            details = card_fetcher.get_card_details(card_name)
            if details:
                card_details.append(details)
    return card_details
