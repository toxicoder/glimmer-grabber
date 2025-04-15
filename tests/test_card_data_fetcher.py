import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import time
from typing import List, Dict, Any
from src.app.card_data_fetcher import CardDataFetcher

class TestCardDataFetcher(unittest.TestCase):
    """Tests for the CardDataFetcher class."""
    def setUp(self) -> None:
        """Set up test environment."""
        self.cache_file: str = "test_cache.json"
        self.fetcher: CardDataFetcher = CardDataFetcher(cache_file=self.cache_file, cache_duration=3600)
        self.mock_card_data: List[Dict[str, Any]] = [{"name": "Card 1", "type": "Action", "set": "Set 1"}]

    def tearDown(self) -> None:
        """Clean up test environment."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    @patch('requests.get')
    def test_fetch_card_data_success(self, mock_get: MagicMock) -> None:
        """Test successful fetching of card data from the API."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_card_data
        self.assertEqual(self.fetcher.fetch_card_data([]), self.mock_card_data)
        self.assertEqual(len(self.fetcher.card_data), 1)

    @patch('requests.get')
    def test_fetch_card_data_failure(self, mock_get: MagicMock) -> None:
        """Test handling of API request failure."""
        mock_get.return_value.status_code = 500
        self.assertEqual(self.fetcher.fetch_card_data([]), [])
        self.assertEqual(len(self.fetcher.card_data), 0)

    @patch('requests.get')
    def test_fetch_card_data_invalid_response(self, mock_get: MagicMock) -> None:
        """Test handling of invalid response format from the API."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"error": "Invalid format"}
        self.assertEqual(self.fetcher.fetch_card_data([]), [])
        self.assertEqual(len(self.fetcher.card_data), 0)

    def test_validate_card_data_success(self) -> None:
        """Test successful validation of card data."""
        card: Dict[str, str] = {"name": "Card 1", "type": "Action", "set": "Set 1"}
        self.assertTrue(self.fetcher.validate_card_data(card))

    def test_validate_card_data_missing_field(self) -> None:
        """Test validation failure due to missing required field."""
        card: Dict[str, str] = {"name": "Card 1", "set": "Set 1"}
        self.assertFalse(self.fetcher.validate_card_data(card))

    @patch('os.path.exists')
    @patch('time.time')
    @patch('os.path.getmtime')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([{"name": "Cached Card", "type": "Character", "set": "Cached Set"}]))
    def test_load_from_cache(self, mock_file: MagicMock, mock_getmtime: MagicMock, mock_time: MagicMock, mock_exists: MagicMock) -> None:
        """Test loading card data from a valid cache file."""
        mock_exists.return_value = True
        mock_time.return_value = 1000  # Simulate current time
        mock_getmtime.return_value = 900  # Simulate cache modified time (within validity)
        self.assertTrue(self.fetcher._load_from_cache())
        self.assertEqual(self.fetcher.card_data, [{"name": "Cached Card", "type": "Character", "set": "Cached Set"}])

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_cache(self, mock_file: MagicMock, mock_get: MagicMock) -> None:
        """Test saving fetched card data to the cache file."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_card_data
        self.fetcher.fetch_card_data([])
        mock_file.assert_called_once_with(self.cache_file, "w")
        mock_file.return_value.write.assert_called_once_with(json.dumps(self.mock_card_data))

    @patch('requests.get')
    def test_fetch_card_data_with_names(self, mock_get: MagicMock) -> None:
        """Test fetching card data with a list of card names."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "type": "Character", "set": "Set 2"},
            {"name": "Card 3", "type": "Item", "set": "Set 1"},
        ]
        card_names: List[str] = ["Card 1", "Card 3"]
        expected_data: List[Dict[str, Any]] = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 3", "type": "Item", "set": "Set 1"},
        ]
        actual_data: List[Dict[str, Any]] = self.fetcher.fetch_card_data(card_names)
        self.assertEqual(actual_data, expected_data)

    @patch('requests.get')
    def test_fetch_card_data_with_empty_names(self, mock_get: MagicMock) -> None:
        """Test fetching card data with an empty list of card names."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "type": "Character", "set": "Set 2"},
            {"name": "Card 3", "type": "Item", "set": "Set 1"},
        ]
        expected_data: List[Dict[str, Any]] = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "type": "Character", "set": "Set 2"},
            {"name": "Card 3", "type": "Item", "set": "Set 1"},
        ]
        actual_data: List[Dict[str, Any]] = self.fetcher.fetch_card_data([])
        self.assertEqual(actual_data, expected_data)

    @patch('requests.get')
    def test_load_and_validate_data(self, mock_get: MagicMock) -> None:
        """Test loading and validating data, including handling of invalid entries."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "set": "Set 2"}  # Missing 'type'
        ]
        self.assertTrue(self.fetcher._load_and_validate_data([]))
        self.assertEqual(len(self.fetcher.card_data), 1)

    @patch('requests.get')
    def test_load_and_validate_data_with_names(self, mock_get: MagicMock) -> None:
        """Test loading and validating data with a list of card names."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "type": "Character", "set": "Set 2"},
            {"name": "Card 3", "type": "Item", "set": "Set 1"},
        ]
        card_names: List[str] = ["Card 1", "Card 3"]
        self.assertTrue(self.fetcher._load_and_validate_data(card_names))
        self.assertEqual(len(self.fetcher.card_data), 2)
        self.assertEqual([card["name"] for card in self.fetcher.card_data], card_names)

if __name__ == "__main__":
    unittest.main()
