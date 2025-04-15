import requests
import json
import time
import os
from typing import List, Dict, Any

CardData = List[Dict[str, Any]]

class CardDataFetcher:
    def __init__(self, api_url: str = "https://lorcanajson.org/", cache_file: str = "card_data_cache.json", cache_duration: int = 3600) -> None:
        self.api_url: str = api_url
        self.cache_file: str = cache_file
        self.cache_duration: int = cache_duration
        self.card_data: CardData = []

    def _is_cache_valid(self) -> bool:
        if not os.path.exists(self.cache_file):
            return False
        modification_time: float = os.path.getmtime(self.cache_file)
        return time.time() - modification_time < self.cache_duration

    def _load_from_cache(self) -> bool:
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

    def _save_to_cache(self) -> bool:
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.card_data, f)
                return True
        except (TypeError, FileNotFoundError) as e:
            print(f"Error saving to cache: {e}")
            return False

    def fetch_card_data(self, card_names: List[str] = []) -> List[Dict[str, Any]]:
        """Fetches card data from the API or loads it from the cache if available and valid.
        This method uses the load_and_validate_data method to ensure only valid card data is returned.
        Args:
            card_names: A list of card names to filter the results.  If empty, all cards are returned.
        Returns:
            A list of validated card data dictionaries, filtered by card_names if provided.
        """
        if self.load_and_validate_data(card_names):
            return self.card_data
        else:
            return []
