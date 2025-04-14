import requests
import json
import time
import os
from typing import List, Dict, Any
"""Fetches card data from an API and manages a local cache."""

CardData = List[Dict[str, Any]]

class CardDataFetcher:
    """Fetches card data from a specified API with caching.

    This class handles fetching card data from an API, caching the data locally to reduce API calls,
    and validating the fetched data.

    Attributes:
        api_url: The URL of the API to fetch data from. Defaults to "https://lorcanajson.org/".
        cache_file: The path to the cache file. Defaults to "card_data_cache.json".
        cache_duration: The duration (in seconds) for which the cache is considered valid. Defaults to 3600 seconds (1 hour).
        card_data: A list to store the fetched card data.
    """
    def __init__(self, api_url: str = "https://lorcanajson.org/", cache_file: str = "card_data_cache.json", cache_duration: int = 3600) -> None:
        """Initializes the CardDataFetcher with the given API URL, cache file, and cache duration.

        Args:
            api_url: The URL of the API.
            cache_file: The path to the cache file.
            cache_duration: The cache validity duration in seconds.
        """
        self.api_url: str = api_url
        self.cache_file: str = cache_file
        self.cache_duration: int = cache_duration
        self.card_data: CardData = []

    def _is_cache_valid(self) -> bool:  # Corrected type hint
        """Checks if the cache file exists and is still valid based on its modification time.

        Returns:
            True if the cache is valid, False otherwise.
        """
        if not os.path.exists(self.cache_file):
            return False
        modification_time: float = os.path.getmtime(self.cache_file)
        return time.time() - modification_time < self.cache_duration

    def _load_from_cache(self) -> bool:  # Corrected type hint
        """Loads card data from the cache file.

        Returns:
            True if data was successfully loaded from the cache, False otherwise.
        """
        try:
            with open(self.cache_file, "r") as f:
                cache_data: Any = json.load(f)
                if isinstance(cache_data, list):
                    self.card_data = cache_data
                    return True
                else:
                    print("Error: Invalid format in cache file.")
                    return False
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading from cache file '{self.cache_file}': {e}")
            return False

    def _save_to_cache(self) -> bool:  # Corrected type hint
        """Saves the current card data to the cache file.

        Returns:
            True if data was successfully saved to the cache, False otherwise.
        """
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.card_data, f)
                return True
        except (TypeError, FileNotFoundError) as e:
            print(f"Error saving to cache: {e}")
            return False

    def fetch_card_data(self, card_names: List[str] = []) -> List[Dict[str, Any]]:
        """Fetches card data from the API or loads it from the cache if available and valid.

        This method first checks if a valid cache exists. If so, it loads the data from the cache.
        Otherwise, it fetches the data from the API and saves it to the cache for future use.
        If card_names are provided, it filters the data to include only those cards.

        Args:
            card_names: A list of card names to filter the results.  If empty, all cards are returned.

        Returns:
            A list of card data dictionaries, filtered by card_names if provided.
        """
        if self._is_cache_valid() and self._load_from_cache():
            if not card_names:
                return self.card_data
            else:
                return [card for card in self.card_data if card.get("name") in card_names]


        try:
            response: requests.Response = requests.get(self.api_url + "cards.json")
            response.raise_for_status()  # Raise an exception for bad status codes
            data: Any = response.json()
            if isinstance(data, list):
                self.card_data = data
                self._save_to_cache()  # Save the fetched data to the cache
                if not card_names:
                    return self.card_data
                else:
                    return [card for card in self.card_data if card.get("name") in card_names]
            else:
                print("Error: Invalid response format from API.")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching card data: {e}")
            return []

    def get_card_data(self) -> CardData:
        """Returns the fetched card data.

        Returns:
            A list of card data dictionaries.
        """
        return self.card_data

    def validate_card_data(self, card: Dict[str, Any]) -> bool:
        """Validates a single card's data.

        Performs basic validation to ensure that the card data contains the required fields.

        Args:
            card: A dictionary representing a card's data.

        Returns:
            True if the card data is valid, False otherwise.
        """
        # Add basic validation - check for required fields
        required_fields: List[str] = ["name", "type", "set"]
        for field in required_fields:
            if field not in card:
                print(f"Validation Error: Missing '{field}' in card data.")
                return False
        return True

    def load_and_validate_data(self, card_names: List[str] = []) -> bool:
        """Loads and validates card data, using the cache if available.

        This method combines fetching (or loading from cache) and validating the card data.

        Args:
            card_names: A list of card names to filter the results. If empty, all cards are loaded and validated.

        Returns:
            True if data loading and validation were successful, False otherwise.
        """
        self.card_data = self.fetch_card_data(card_names)
        if self.card_data:
            validated_data: CardData = []
            for card in self.card_data:
                if self.validate_card_data(card):
                    validated_data.append(card)
            self.card_data = validated_data
            return True
        return False
