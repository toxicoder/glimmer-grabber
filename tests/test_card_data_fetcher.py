import unittest
from unittest.mock import patch, mock_open
import json
import os
import time
from src.glimmer_grabber.card_data_fetcher import CardDataFetcher

class TestCardDataFetcher(unittest.TestCase):
    def setUp(self):
        self.cache_file = "test_cache.json"
        self.fetcher = CardDataFetcher(cache_file=self.cache_file, cache_duration=3600)
        self.mock_card_data = [{"name": "Card 1", "type": "Action", "set": "Set 1"}]

    def tearDown(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    @patch('requests.get')
    def test_fetch_card_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_card_data
        self.assertTrue(self.fetcher.fetch_card_data())
        self.assertEqual(len(self.fetcher.get_card_data()), 1)

    @patch('requests.get')
    def test_fetch_card_data_failure(self, mock_get):
        mock_get.return_value.status_code = 500
        self.assertFalse(self.fetcher.fetch_card_data())
        self.assertEqual(len(self.fetcher.get_card_data()), 0)

    @patch('requests.get')
    def test_fetch_card_data_invalid_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"error": "Invalid format"}
        self.assertFalse(self.fetcher.fetch_card_data())
        self.assertEqual(len(self.fetcher.get_card_data()), 0)

    def test_validate_card_data_success(self):
        card = {"name": "Card 1", "type": "Action", "set": "Set 1"}
        self.assertTrue(self.fetcher.validate_card_data(card))

    def test_validate_card_data_missing_field(self):
        card = {"name": "Card 1", "set": "Set 1"}
        self.assertFalse(self.fetcher.validate_card_data(card))

    @patch('requests.get')
    def test_load_and_validate_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "set": "Set 2"}  # Missing 'type'
        ]
        self.assertTrue(self.fetcher.load_and_validate_data())
        self.assertEqual(len(self.fetcher.get_card_data()), 1)  # Only one valid card

    @patch('os.path.exists')
    @patch('time.time')
    @patch('os.path.getmtime')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([{"name": "Cached Card", "type": "Character", "set": "Cached Set"}]))
    def test_load_from_cache(self, mock_file, mock_getmtime, mock_time, mock_exists):
        mock_exists.return_value = True
        mock_time.return_value = 1000  # Simulate current time
        mock_getmtime.return_value = 900  # Simulate cache modified time (within validity)
        self.assertTrue(self.fetcher._load_from_cache())
        self.assertEqual(self.fetcher.get_card_data(), [{"name": "Cached Card", "type": "Character", "set": "Cached Set"}])

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_cache(self, mock_file, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_card_data
        self.fetcher.fetch_card_data()
        mock_file.assert_called_once_with(self.cache_file, "w")
        mock_file.return_value.write.assert_called_once_with(json.dumps(self.mock_card_data))

if __name__ == "__main__":
    unittest.main()
