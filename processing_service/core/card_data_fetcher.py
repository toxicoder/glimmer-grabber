import redis
import requests
import json
from shared.config import get_settings

settings = get_settings()

class CardDataFetcher:
    def __init__(self) -> None:
        self.redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def get_card_details(self, card_name: str) -> dict:
        """
        Fetches card details from the cache or the Lorcana API.
        """
        try:
            cached_data = self.redis_client.get(card_name)
            if cached_data:
                return json.loads(cached_data)
        except redis.exceptions.RedisError as e:
            print(f"Redis error: {e}")
            # Fallback to API if Redis fails
            pass

        try:
            response = requests.get(f"{settings.lorcana_api_url}/cards/{card_name}")
            response.raise_for_status()
            card_details = response.json()
            if response.status_code == 200 and card_details:
                try:
                    self.redis_client.set(card_name, json.dumps(card_details))
                except redis.exceptions.RedisError as e:
                    print(f"Redis error: {e}")
            return card_details
        except requests.exceptions.RequestException as e:
            print(f"Error calling Lorcana API: {e}")
            return None
