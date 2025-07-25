import unittest
from unittest.mock import patch, MagicMock
import requests
from processing_service.core.card_data_fetcher import CardDataFetcher

class TestCardDataFetcher(unittest.TestCase):

    @patch('redis.Redis')
    @patch('processing_service.core.card_data_fetcher.get_settings')
    def setUp(self, mock_get_settings, mock_redis):
        mock_settings = MagicMock()
        mock_settings.redis_host = "localhost"
        mock_settings.redis_port = 6379
        mock_get_settings.return_value = mock_settings
        self.mock_redis_instance = mock_redis.return_value
        self.fetcher = CardDataFetcher()

    @patch('requests.get')
    def test_fetch_card_data_from_api_success(self, mock_get):
        self.mock_redis_instance.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Data": [{"CardName": "Test Card"}]}
        mock_get.return_value = mock_response

        card_name = "Test Card"
        result = self.fetcher.get_card_details(card_name)

        self.assertEqual(result, {"Data": [{"CardName": "Test Card"}]})
        self.mock_redis_instance.set.assert_called_once()

    @patch('requests.get')
    def test_fetch_card_data_from_api_failure(self, mock_get):
        self.mock_redis_instance.get.return_value = None
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_get.return_value = mock_response

        card_name = "Nonexistent Card"
        result = self.fetcher.get_card_details(card_name)

        self.assertIsNone(result)

    def test_fetch_card_data_from_cache(self):
        card_name = "Cached Card"
        cached_data = '{"CardName": "Cached Card"}'
        self.mock_redis_instance.get.return_value = cached_data.encode('utf-8')

        result = self.fetcher.get_card_details(card_name)

        self.assertEqual(result, {"CardName": "Cached Card"})
        self.mock_redis_instance.get.assert_called_once_with(card_name)

if __name__ == '__main__':
    unittest.main()
