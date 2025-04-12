import unittest
from unittest.mock import patch
from card_data_fetcher import CardDataFetcher

class TestCardDataFetcher(unittest.TestCase):
    @patch('requests.get')
    def test_fetch_card_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"name": "Card 1", "type": "Action", "set": "Set 1"}]
        fetcher = CardDataFetcher()
        self.assertTrue(fetcher.fetch_card_data())
        self.assertEqual(len(fetcher.get_card_data()), 1)

    @patch('requests.get')
    def test_fetch_card_data_failure(self, mock_get):
        mock_get.return_value.status_code = 500
        fetcher = CardDataFetcher()
        self.assertFalse(fetcher.fetch_card_data())
        self.assertEqual(len(fetcher.get_card_data()), 0)

    @patch('requests.get')
    def test_fetch_card_data_invalid_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"error": "Invalid format"}
        fetcher = CardDataFetcher()
        self.assertFalse(fetcher.fetch_card_data())
        self.assertEqual(len(fetcher.get_card_data()), 0)

    def test_validate_card_data_success(self):
        fetcher = CardDataFetcher()
        card = {"name": "Card 1", "type": "Action", "set": "Set 1"}
        self.assertTrue(fetcher.validate_card_data(card))

    def test_validate_card_data_missing_field(self):
        fetcher = CardDataFetcher()
        card = {"name": "Card 1", "set": "Set 1"}
        self.assertFalse(fetcher.validate_card_data(card))

    @patch('requests.get')
    def test_load_and_validate_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Card 1", "type": "Action", "set": "Set 1"},
            {"name": "Card 2", "set": "Set 2"}  # Missing 'type'
        ]
        fetcher = CardDataFetcher()
        self.assertTrue(fetcher.load_and_validate_data())
        self.assertEqual(len(fetcher.get_card_data()), 1)  # Only one valid card

if __name__ == "__main__":
    unittest.main()
