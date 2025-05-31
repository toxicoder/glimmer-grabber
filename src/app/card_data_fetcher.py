# Standard library imports
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional # Added Optional

# Third-party imports
import requests

# Application-specific imports
from src.app.exceptions import APIFetchError, CacheError, DataFormatError
from src.app.config_manager import ConfigManager # Import ConfigManager

# Type alias for card data structure
CardData = List[Dict[str, Any]]

# Module-level logger
logger = logging.getLogger(__name__)

class CardDataFetcher:
    """
    Fetches card data from an external API, with support for caching results.
    ... (docstring mostly same)
    Attributes:
        config_manager (ConfigManager): Manages application configuration.
        api_url (str): The URL of the API endpoint.
        cache_file (str): The file path for the cache.
        cache_duration (int): Cache validity duration in seconds.
    """
    def __init__(self,
                 config_manager: Optional[ConfigManager] = None,
                 api_url: Optional[str] = None,
                 cache_file: Optional[str] = None,
                 cache_duration: Optional[int] = None) -> None:
        """
        Initializes the CardDataFetcher.
        Settings are primarily sourced from ConfigManager. Explicit arguments can override.

        Args:
            config_manager (Optional[ConfigManager]): An instance of ConfigManager.
                                                      If None, a default one is created.
            api_url (Optional[str]): API URL. Overrides ConfigManager if provided.
            cache_file (Optional[str]): Path to cache file. Overrides ConfigManager if provided.
                                        If None, constructed using ConfigManager's output_path and default cache_file_name.
            cache_duration (Optional[int]): Cache duration. Overrides ConfigManager if provided.
        """
        self.config_manager = config_manager if config_manager is not None else ConfigManager()

        # Prioritize direct arguments, then ConfigManager's settings
        self.api_url: str = api_url if api_url is not None else self.config_manager.get_api_url()

        # Determine cache_file path:
        # 1. Use direct `cache_file` argument if provided.
        # 2. Else, construct from ConfigManager's output_path and default cache_file_name.
        if cache_file is not None:
            self.cache_file: str = cache_file
        else:
            output_dir_from_config = self.config_manager.get_output_path()
            default_cache_filename = self.config_manager.get_cache_file_name()
            if output_dir_from_config: # If output_path is configured
                # Ensure output directory exists for the cache file
                # os.makedirs(output_dir_from_config, exist_ok=True) # Moved to _save_to_cache
                self.cache_file: str = os.path.join(output_dir_from_config, default_cache_filename)
            else:
                # Fallback if output_path is not set (e.g. ConfigManager used standalone without CLI context)
                logger.warning("Output directory not set in ConfigManager; defaulting cache file to be relative to current directory.")
                self.cache_file: str = default_cache_filename

        self.cache_duration: int = cache_duration if cache_duration is not None else self.config_manager.get_cache_duration()

        logger.debug(f"CardDataFetcher initialized: API URL='{self.api_url}', Cache File='{self.cache_file}', Cache Duration={self.cache_duration}s")

    def _is_cache_valid(self) -> bool:
        """
        Checks if the existing cache file is present and still valid based on its modification time.

        Returns:
            bool: True if a valid cache file exists, False otherwise.
        """
        # Check if cache file exists
        if not os.path.exists(self.cache_file):
            logger.info(f"Cache file '{self.cache_file}' not found. Cache is invalid.")
            return False

        try:
            # Get the last modification time of the cache file
            modification_time: float = os.path.getmtime(self.cache_file)
            # Check if current time minus modification time is less than cache duration
            is_valid = (time.time() - modification_time) < self.cache_duration
            if is_valid:
                logger.info(f"Cache file '{self.cache_file}' is present and valid.")
            else:
                logger.info(f"Cache file '{self.cache_file}' is present but expired.")
            return is_valid
        except FileNotFoundError:
            # This case should ideally be covered by os.path.exists, but included for robustness
            logger.warning(f"Cache file '{self.cache_file}' disappeared during mtime check. Cache is invalid.")
            return False
        except Exception as e:
            # Log any other errors during cache validity check
            logger.error(f"Error checking cache validity for '{self.cache_file}': {e}", exc_info=True)
            return False # Treat as invalid on error

    def _load_from_cache(self) -> CardData:
        """
        Loads card data from the cache file.

        Returns:
            CardData: The list of card data dictionaries loaded from the cache.

        Raises:
            CacheError: If the cache file is not found, cannot be read, or if the
                        JSON data is malformed or not in the expected list format.
            DataFormatError: If the data in the cache file is not a list (the expected top-level type).
        """
        logger.info(f"Attempting to load card data from cache file: {self.cache_file}")
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f: # Specify encoding
                cache_data: Any = json.load(f)
                # Validate that the loaded data is a list
                if not isinstance(cache_data, list):
                    logger.error(f"Invalid format in cache file '{self.cache_file}'. Expected a list, got {type(cache_data)}.")
                    raise DataFormatError(f"Invalid format in cache file '{self.cache_file}'. Expected a list.")
                logger.info(f"Successfully loaded {len(cache_data)} items from cache file '{self.cache_file}'.")
                return cache_data
        except FileNotFoundError:
            logger.error(f"Cache file '{self.cache_file}' not found during load attempt.")
            raise CacheError(f"Cache file '{self.cache_file}' not found.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from cache file '{self.cache_file}': {e}", exc_info=True)
            raise CacheError(f"Error decoding JSON from cache file '{self.cache_file}': {e}")
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred while loading from cache '{self.cache_file}': {e}", exc_info=True)
            raise CacheError(f"An unexpected error occurred while loading from cache '{self.cache_file}': {e}")

    def _save_to_cache(self, card_data: CardData) -> None:
        """
        Saves the provided card data to the cache file.

        Args:
            card_data (CardData): The list of card data dictionaries to save.

        Raises:
            CacheError: If an error occurs during file writing or JSON serialization.
        """
        logger.info(f"Attempting to save {len(card_data)} items to cache file: {self.cache_file}")
        try:
            # Ensure the directory for the cache file exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f: # Specify encoding
                json.dump(card_data, f, indent=4) # Save with indent for readability
            logger.info(f"Successfully saved card data to cache file '{self.cache_file}'.")
        except (TypeError, FileNotFoundError, IOError) as e: # More specific IO errors
            logger.error(f"Error saving to cache file '{self.cache_file}': {e}", exc_info=True)
            raise CacheError(f"Error saving to cache file '{self.cache_file}': {e}")
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred while saving to cache '{self.cache_file}': {e}", exc_info=True)
            raise CacheError(f"An unexpected error occurred while saving to cache '{self.cache_file}': {e}")

    def fetch_card_data(self, card_names: List[str] = []) -> CardData:
        """
        Fetches card data, utilizing cache if valid, otherwise from the API.

        This is the primary public method. It first checks the cache. If a valid
        cache exists, data is loaded from it. Otherwise, it fetches data from the
        API, validates it, and then saves it to the cache for future use.
        The returned data can be filtered by a list of card names.

        Args:
            card_names (List[str]): A list of card names to filter the results.
                                    If empty, all cards from the source (cache or API)
                                    are returned after validation.

        Returns:
            CardData: A list of validated card data dictionaries. This list may be
                      filtered by `card_names`.

        Raises:
            APIFetchError: If there's an issue fetching data from the API (e.g., network error,
                           bad HTTP response, or unexpected error during the fetch process).
            CacheError: If there's an issue with cache read/write operations that prevents
                        data retrieval or persistence.
            DataFormatError: If data from the API or cache is in an unexpected format
                             (e.g., not a list, or items are not dictionaries).
        """
        logger.debug(f"Fetching card data. Requested card names: {card_names if card_names else 'all cards'}")
        try:
            # Delegate the core logic to _load_and_validate_data
            return self._load_and_validate_data(card_names)
        except (APIFetchError, CacheError, DataFormatError) as e:
            # Log known exceptions from the core logic and re-raise them
            logger.error(f"Failed to fetch card data due to a known application error: {e}", exc_info=True)
            raise
        except Exception as e:
            # Log unexpected exceptions and wrap them in a generic APIFetchError for consistency
            logger.error(f"An unexpected error occurred in fetch_card_data: {e}", exc_info=True)
            raise APIFetchError(f"An unexpected error occurred during data fetching: {e}")

    def _validate_card_data_entry(self, card: Dict[str, Any]) -> bool:
        """
        Validates a single card data dictionary entry.

        Checks for the presence of essential fields required for the application
        to consider a card entry valid.

        Args:
            card (Dict[str, Any]): The card data dictionary to validate.

        Returns:
            bool: True if the card entry is valid, False otherwise.
        """
        # Define essential fields for a card entry to be considered valid
        required_fields = ["name", "type", "set"]
        is_valid = all(field in card for field in required_fields)
        if not is_valid:
            missing_fields = [field for field in required_fields if field not in card]
            logger.warning(f"Card data entry failed validation. Entry: {card.get('name', 'N/A')}, Missing fields: {missing_fields}")
        return is_valid

    def _load_and_validate_data(self, card_names: List[str] = []) -> CardData:
        """
        Core logic to load data from cache or API, validate, and filter it.

        This method first attempts to load from a valid cache. If caching fails or
        is invalid, it fetches from the API, validates the new data, and saves it
        to the cache. Finally, it filters the data based on `card_names`.

        Args:
            card_names (List[str]): A list of card names for filtering.

        Returns:
            CardData: The validated and potentially filtered list of card data.

        Raises:
            APIFetchError: For API-related fetch failures.
            CacheError: For cache-related read/write failures.
            DataFormatError: If data format is invalid from cache or API.
        """
        # Attempt to load from cache if it's valid
        if self._is_cache_valid():
            try:
                logger.info(f"Attempting to load data from valid cache: {self.cache_file}")
                cached_data = self._load_from_cache() # Might raise CacheError or DataFormatError

                # Ensure all items in cached_data are dictionaries (structural integrity)
                if not all(isinstance(item, dict) for item in cached_data):
                    logger.error("Cached data contains items that are not dictionaries. Invalidating cache content.")
                    raise DataFormatError("Cache contains items that are not dictionaries.")

                # Validate individual card entries from cache
                validated_data = [card for card in cached_data if self._validate_card_data_entry(card)]
                if len(validated_data) != len(cached_data):
                    logger.warning(f"Some card entries from cache failed validation. Loaded {len(validated_data)} valid entries out of {len(cached_data)} total in cache.")

                logger.info(f"Successfully loaded and validated {len(validated_data)} card entries from cache.")

                # Filter data if card_names are provided
                if not card_names:
                    return validated_data
                else:
                    # Assumes card dictionaries have a "name" key for filtering
                    filtered_data = [card for card in validated_data if card.get("name") in card_names]
                    logger.debug(f"Filtered cached data by {len(card_names)} names, resulting in {len(filtered_data)} entries.")
                    return filtered_data
            except (CacheError, DataFormatError) as e:
                # If loading from cache fails (e.g. corrupted file, format error), log and fall through to API fetch
                logger.warning(f"Cache error during load and validate: {e}. Attempting API fetch.", exc_info=True)
            # Fall through to API fetch if cache is invalid or loading/validation failed

        # Fetch data from API if cache was not used or failed
        logger.info(f"Fetching data from API: {self.api_url}")
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            logger.debug(f"API request to {self.api_url} successful (status code {response.status_code}).")

            api_data_raw = response.json() # Might raise json.JSONDecodeError

            # Validate top-level API response structure
            if not isinstance(api_data_raw, list):
                logger.error(f"Invalid data format from API: Expected a list, got {type(api_data_raw)}.")
                raise DataFormatError(f"Invalid data format from API: Expected a list, got {type(api_data_raw)}.")
            logger.debug(f"Received {len(api_data_raw)} items from API before validation.")

            # Validate individual card entries from API response
            validated_api_data = []
            for card_item in api_data_raw:
                if not isinstance(card_item, dict): # Ensure each item is a dictionary
                     logger.warning(f"API returned an item that is not a dictionary: {card_item}. Skipping.")
                     continue
                if self._validate_card_data_entry(card_item):
                    validated_api_data.append(card_item)
                else:
                    # Warning for specific entry logged in _validate_card_data_entry
                    logger.debug(f"Skipping API card entry that failed validation: {card_item.get('name', 'N/A')}")

            logger.info(f"Validated {len(validated_api_data)} card entries from API (out of {len(api_data_raw)} received).")

            # Save the newly fetched and validated data to cache
            self._save_to_cache(validated_api_data) # Might raise CacheError

            # Filter data if card_names are provided
            if not card_names:
                return validated_api_data
            else:
                filtered_data = [card for card in validated_api_data if card.get("name") in card_names]
                logger.debug(f"Filtered API data by {len(card_names)} names, resulting in {len(filtered_data)} entries.")
                return filtered_data

        except requests.RequestException as e: # Covers network errors, timeouts, etc.
            logger.error(f"API request to {self.api_url} failed: {e}", exc_info=True)
            raise APIFetchError(f"API request failed: {e}")
        except json.JSONDecodeError as e: # If API response is not valid JSON
            logger.error(f"Failed to decode JSON from API response ({self.api_url}): {e}", exc_info=True)
            raise DataFormatError(f"Failed to decode JSON from API response: {e}")
        # Other exceptions (CacheError from _save_to_cache, DataFormatError) will propagate