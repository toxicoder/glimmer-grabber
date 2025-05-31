import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import time
from typing import List, Dict, Any, Optional # Added Optional
from src.app.card_data_fetcher import CardDataFetcher, CardData # Import CardData type alias
from src.app.config_manager import ConfigManager
from src.app.exceptions import APIFetchError, CacheError, DataFormatError

class TestCardDataFetcher(unittest.TestCase):
    """Tests for the CardDataFetcher class."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

        self.mock_output_path = self.test_dir.name
        self.default_cache_file_name = "default_test_cache.json"
        self.custom_cache_file_path = os.path.join(self.mock_output_path, "custom_cache.json")

        # Base mock config for ConfigManager
        self.base_config_data = {
            "output_path": self.mock_output_path,
            "api_url": "http://fakeapi.com/cards",
            "cache_file_name": self.default_cache_file_name,
            "cache_duration": 3600,
        }

        # Create a ConfigManager instance with these base settings
        # No CLI args means these will be taken as is.
        self.mock_config_manager = ConfigManager(cli_args=argparse.Namespace(
            output_dir=self.mock_output_path,
            api_url=self.base_config_data["api_url"],
            cache_duration=self.base_config_data["cache_duration"]
            # other CLI args can be None or default
        ))
        # Ensure output_path is set in the mock_config_manager's internal config
        self.mock_config_manager.config["output_path"] = self.mock_output_path
        self.mock_config_manager.config["cache_file_name"] = self.default_cache_file_name


        # Default fetcher uses ConfigManager implicitly for some settings if not overridden
        self.fetcher_with_config_manager = CardDataFetcher(config_manager=self.mock_config_manager)
        # This fetcher will use the path constructed from mock_config_manager's output_path
        self.expected_cache_path_from_config = os.path.join(self.mock_output_path, self.default_cache_file_name)

        self.mock_api_card_data: CardData = [
            {"name": "Card 1 API", "type": "Action", "set": "Set 1 API"},
            {"name": "Card 2 API", "type": "Character", "set": "Set 2 API"}
        ]
        self.mock_cache_card_data: CardData = [
            {"name": "Card 1 Cache", "type": "Item", "set": "Set 1 Cache"}
        ]

    # --- Test Initialization ---
    def test_init_with_direct_args(self):
        """Test CardDataFetcher initialization with direct arguments."""
        fetcher = CardDataFetcher(
            api_url="http://direct-url.com",
            cache_file=self.custom_cache_file_path,
            cache_duration=1000
        )
        self.assertEqual(fetcher.api_url, "http://direct-url.com")
        self.assertEqual(fetcher.cache_file, self.custom_cache_file_path)
        self.assertEqual(fetcher.cache_duration, 1000)

    def test_init_with_config_manager(self):
        """Test CardDataFetcher initialization using a ConfigManager instance."""
        self.assertEqual(self.fetcher_with_config_manager.api_url, self.base_config_data["api_url"])
        self.assertEqual(self.fetcher_with_config_manager.cache_file, self.expected_cache_path_from_config)
        self.assertEqual(self.fetcher_with_config_manager.cache_duration, self.base_config_data["cache_duration"])

    def test_init_config_manager_overrides_direct_args_if_direct_are_none(self):
        """Test that ConfigManager values are used if direct args are None."""
        # Pass None for direct args, so it should fallback to config_manager's values
        fetcher = CardDataFetcher(
            config_manager=self.mock_config_manager,
            api_url=None,
            cache_file=None,
            cache_duration=None
        )
        self.assertEqual(fetcher.api_url, self.base_config_data["api_url"])
        self.assertEqual(fetcher.cache_file, self.expected_cache_path_from_config)
        self.assertEqual(fetcher.cache_duration, self.base_config_data["cache_duration"])

    # --- Test Cache Logic ---
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    @patch('time.time')
    def test_is_cache_valid_true(self, mock_time, mock_getmtime, mock_exists):
        """Test _is_cache_valid returns True for a recent, existing cache file."""
        mock_exists.return_value = True
        mock_getmtime.return_value = 9000
        mock_time.return_value = 9000 + self.fetcher_with_config_manager.cache_duration - 60 # 60s before expiry

        self.assertTrue(self.fetcher_with_config_manager._is_cache_valid())
        mock_exists.assert_called_once_with(self.expected_cache_path_from_config)

    @patch('os.path.exists', return_value=False)
    def test_is_cache_valid_false_no_file(self, mock_exists):
        """Test _is_cache_valid returns False if cache file does not exist."""
        self.assertFalse(self.fetcher_with_config_manager._is_cache_valid())

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getmtime')
    @patch('time.time')
    def test_is_cache_valid_false_expired(self, mock_time, mock_getmtime, mock_exists):
        """Test _is_cache_valid returns False if cache file is expired."""
        mock_getmtime.return_value = 9000
        mock_time.return_value = 9000 + self.fetcher_with_config_manager.cache_duration + 60 # 60s after expiry
        self.assertFalse(self.fetcher_with_config_manager._is_cache_valid())

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_cache_success(self, mock_file_open):
        """Test successful saving of data to cache."""
        self.fetcher_with_config_manager._save_to_cache(self.mock_api_card_data)
        mock_file_open.assert_called_once_with(self.expected_cache_path_from_config, "w", encoding="utf-8")
        # Check that json.dump was called with the correct data and indent
        # The actual call is to `json.dump(card_data, f, indent=4)`
        # We need to access the file handle `f` from the mock_file_open context manager
        # and then check its write calls, or check args of json.dump if we patched it.
        # For simplicity, assume if open is correct, dump is likely correct for now or test via integration.
        # A more precise way would be to patch json.dump.
        handle = mock_file_open()
        expected_json_string = json.dumps(self.mock_api_card_data, indent=4)
        handle.write.assert_called_once_with(expected_json_string)


    @patch('builtins.open', side_effect=IOError("Failed to write"))
    def test_save_to_cache_io_error(self, mock_file_open):
        """Test _save_to_cache raises CacheError on IOError."""
        with self.assertRaises(CacheError) as context:
            self.fetcher_with_config_manager._save_to_cache(self.mock_api_card_data)
        self.assertIn("Failed to write", str(context.exception))

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_load_from_cache_json_decode_error(self, mock_file_open):
        """Test _load_from_cache raises CacheError on JSONDecodeError."""
        with self.assertRaises(CacheError) as context:
            self.fetcher_with_config_manager._load_from_cache()
        self.assertIn("Error decoding JSON", str(context.exception))

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "not a list"}')
    def test_load_from_cache_data_format_error(self, mock_file_open):
        """Test _load_from_cache raises DataFormatError if cache is not a list."""
        with self.assertRaises(DataFormatError) as context:
            self.fetcher_with_config_manager._load_from_cache()
        self.assertIn("Expected a list", str(context.exception))

    # --- Test API Fetching Logic ---
    @patch('requests.get')
    @patch('src.app.card_data_fetcher.CardDataFetcher._is_cache_valid', return_value=False) # Ensure API is called
    def test_fetch_from_api_success(self, mock_cache_valid, mock_requests_get):
        """Test successful data fetching from API when cache is invalid."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_card_data
        mock_requests_get.return_value = mock_response

        with patch.object(self.fetcher_with_config_manager, '_save_to_cache') as mock_save_cache:
            fetched_data = self.fetcher_with_config_manager.fetch_card_data(["Card 1 API"])

            mock_requests_get.assert_called_once_with(self.base_config_data["api_url"])
            mock_save_cache.assert_called_once_with(self.mock_api_card_data) # Save all validated API data

            # Expecting only "Card 1 API" due to filtering
            self.assertEqual(len(fetched_data), 1)
            self.assertEqual(fetched_data[0]["name"], "Card 1 API")

    @patch('requests.get')
    @patch('src.app.card_data_fetcher.CardDataFetcher._is_cache_valid', return_value=False)
    def test_fetch_from_api_http_error(self, mock_cache_valid, mock_requests_get):
        """Test API fetch raises APIFetchError on HTTP error status."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_requests_get.return_value = mock_response

        with self.assertRaises(APIFetchError):
            self.fetcher_with_config_manager.fetch_card_data([])

    @patch('requests.get', side_effect=requests.exceptions.RequestException("Network Error"))
    @patch('src.app.card_data_fetcher.CardDataFetcher._is_cache_valid', return_value=False)
    def test_fetch_from_api_request_exception(self, mock_cache_valid, mock_requests_get):
        """Test API fetch raises APIFetchError on requests.RequestException."""
        with self.assertRaises(APIFetchError):
            self.fetcher_with_config_manager.fetch_card_data([])

    @patch('requests.get')
    @patch('src.app.card_data_fetcher.CardDataFetcher._is_cache_valid', return_value=False)
    def test_fetch_from_api_invalid_json_response(self, mock_cache_valid, mock_requests_get):
        """Test API fetch raises DataFormatError for invalid JSON from API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Error", "doc", 0)
        mock_requests_get.return_value = mock_response

        with self.assertRaises(DataFormatError):
            self.fetcher_with_config_manager.fetch_card_data([])

    @patch('requests.get')
    @patch('src.app.card_data_fetcher.CardDataFetcher._is_cache_valid', return_value=False)
    def test_fetch_from_api_response_not_a_list(self, mock_cache_valid, mock_requests_get):
        """Test API fetch raises DataFormatError if API response is not a list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "not a list"} # API returns a dict instead of list
        mock_requests_get.return_value = mock_response

        with self.assertRaises(DataFormatError):
            self.fetcher_with_config_manager.fetch_card_data([])


    # --- Test Combined Logic (Cache + API + Validation) ---
    @patch('os.path.exists', return_value=True)
    @patch('os.path.getmtime')
    @patch('time.time')
    @patch('builtins.open', new_callable=mock_open)
    def test_fetch_data_uses_valid_cache(self, mock_file_open, mock_time, mock_getmtime, mock_path_exists):
        """Test that valid cached data is returned and API is not called."""
        mock_getmtime.return_value = time.time() - 1000 # Cache is 1000s old, well within 3600s duration

        # Prepare mock_open to return cached data
        valid_cached_content = [
            {"name": "Cached Valid Card", "type": "Character", "set": "Cache Set"},
            {"name": "Another Cached Card", "type": "Action", "set": "Cache Set"}
        ]
        mock_file_open.return_value.read.return_value = json.dumps(valid_cached_content)

        with patch('requests.get') as mock_requests_get: # Monitor if API is called
            fetched_data = self.fetcher_with_config_manager.fetch_card_data(["Cached Valid Card"])

            mock_requests_get.assert_not_called() # API should not be called
            self.assertEqual(len(fetched_data), 1)
            self.assertEqual(fetched_data[0]["name"], "Cached Valid Card")

    @patch('requests.get')
    @patch('src.app.card_data_fetcher.CardDataFetcher._is_cache_valid', return_value=True)
    @patch('src.app.card_data_fetcher.CardDataFetcher._load_from_cache') # Mock this to raise error
    def test_fetch_data_api_on_cache_read_error(self, mock_load_cache, mock_is_valid, mock_requests_get):
        """Test API fetch if cache is valid but reading it fails (e.g. CacheError)."""
        mock_load_cache.side_effect = CacheError("Failed to read cache file")

        mock_api_response = MagicMock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = self.mock_api_card_data
        mock_requests_get.return_value = mock_api_response

        with patch.object(self.fetcher_with_config_manager, '_save_to_cache') as mock_save_cache:
            fetched_data = self.fetcher_with_config_manager.fetch_card_data([])
            mock_requests_get.assert_called_once() # API should be called
            mock_save_cache.assert_called_once_with(self.mock_api_card_data)
            self.assertEqual(fetched_data, self.mock_api_card_data)

    def test_validate_card_data_entry(self):
        """Test _validate_card_data_entry method."""
        valid_card = {"name": "Test", "type": "Test", "set": "Test"}
        invalid_card_missing_type = {"name": "Test", "set": "Test"}

        self.assertTrue(self.fetcher_with_config_manager._validate_card_data_entry(valid_card))
        self.assertFalse(self.fetcher_with_config_manager._validate_card_data_entry(invalid_card_missing_type))
        # Test with an empty dict
        self.assertFalse(self.fetcher_with_config_manager._validate_card_data_entry({}))


if __name__ == "__main__":
    unittest.main()
