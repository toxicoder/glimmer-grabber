import requests
import json
from typing import List, Dict, Any

class CardDataFetcher:
    """
    Fetches card data from a specified API.

    Attributes:
        api_url (str): The URL of the API to fetch data from. Defaults to "https://lorcanajson.org/".
        card_data (List[Dict[str, Any]]): A list to store the fetched card data.
    """
    def __init__(self, api_url: str = "https://lorcanajson.org/") -> None:
        """
        Initializes the CardDataFetcher with the given API URL.

        Args:
            api_url (str): The URL of the API.
        """
        self.api_url = api_url
        self.card_data: List[Dict[str, Any]] = []

    def fetch_card_data(self) -> bool:
        """
        Fetches card data from the API.

        Returns:
            bool: True if data fetching was successful, False otherwise.
        """
        try:
            response = requests.get(self.api_url + "cards.json")
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            if isinstance(data, list):
                self.card_data = data
                return True
            else:
                print("Error: Invalid response format from API.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error fetching card data: {e}")
            return False

    def get_card_data(self) -> List[Dict[str, Any]]:
        """
        Returns the fetched card data.

        Returns:
            List[Dict[str, Any]]: A list of card data dictionaries.
        """
        return self.card_data

    def validate_card_data(self, card: Dict[str, Any]) -> bool:
        """
        Validates a single card's data.

        Args:
            card (Dict[str, Any]): A dictionary representing a card's data.

        Returns:
            bool: True if the card data is valid, False otherwise.
        """
        # Add basic validation - check for required fields
        required_fields = ["name", "type", "set"]
        for field in required_fields:
            if field not in card:
                print(f"Validation Error: Missing '{field}' in card data.")
                return False
        return True

    def load_and_validate_data(self) -> bool:
        """
        Fetches, loads, and validates card data.

        Returns:
            bool: True if data loading and validation were successful, False otherwise.
        """
        if self.fetch_card_data():
            validated_data: List[Dict[str, Any]] = []
            for card in self.card_data:
                if self.validate_card_data(card):
                    validated_data.append(card)
            self.card_data = validated_data
            return True
        return False
