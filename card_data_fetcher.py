import requests
import json
import time
import os
from typing import List, Dict, Any

class CardDataFetcher:
    """
    Fetches card data from a specified API with caching.

    Attributes:
        api_url (str): The URL of the API to fetch data from. Defaults to "https://lorcanajson.org/".
        cache_file (str): The path to the cache file. Defaults to "card_data_cache.json".
        cache_duration (int): The duration (in seconds) for which the cache is considered valid. Defaults to 3600 seconds (1 hour).
        card_data (List[Dict[str, Any]]): A list to store the fetched card data.
    """
    def __init__(self, api_url: str = "https://lorcanajson.org/", cache_file: str = "card_data_cache.json", cache_duration: int = 3600) -> None:
        """
        Initializes the CardDataFetcher with the given API URL, cache file, and cache duration.

        Args:
            api_url (str): The URL of the API.
            cache_file (str): The path to the cache file.
            cache_duration (int): The cache validity duration in seconds.
        """
        self.api_url = api_url
        self.cache_file = cache_file
        self.cache_duration = cache_duration
        self.card_data: List[Dict[str, Any]] = []

    def _is_cache_valid(self) -> bool:
        """
        Checks if the cache file exists and is still valid based on its modification time.

        Returns:
            bool: True if the cache is valid, False otherwise.
        """
        if not os.path.exists(self.cache_file):
            return False
        modification_time = os.path.getmtime(self.cache_file)
        return time.time() - modification_time < self.cache_duration

    def _load_from_cache(self) -> bool:
        """
        Loads card data from the cache file.

        Returns:
            bool: True if data was successfully loaded from the cache, False otherwise.
        """
        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)
                if isinstance(cache_data, list):
                    self.card_data = cache_data
                    return True
                else:
                    print("Error: Invalid format in cache file.")
                    return False
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading from cache file '{self.cache_file}': {e}")
            return False

    def _save_to_cache(self) -> bool:
        """
        Saves the current card data to the cache file.

        Returns:
            bool: True if data was successfully saved to the cache, False otherwise.
        """
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.card_data, f)
                return True
        except (TypeError, FileNotFoundError) as e:
            print(f"Error saving to cache: {e}")
            return False

    def fetch_card_data(self) -> bool:
        """
        Fetches card data from the API or loads it from the cache if available and valid.

        Returns:
            bool: True if data fetching or loading was successful, False otherwise.
        """
        if self._is_cache_valid() and self._load_from_cache():
            return True

        try:
            response = requests.get(self.api_url + "cards.json")
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            if isinstance(data, list):
                self.card_data = data
                self._save_to_cache()  # Save the fetched data to the cache
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
        Loads and validates card data, using the cache if available.

        Returns:
            bool: True if data loading and validation were successful, False otherwise.
        """
        if self.fetch_card_data():  # This now uses the cache
            validated_data: List[Dict[str, Any]] = []
            for card in self.card_data:
                if self.validate_card_data(card):
                    validated_data.append(card)
            self.card_data = validated_data
            return True
        return False
