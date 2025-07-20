import os
import redis
import requests
import json

LORCANA_API_URL = os.environ.get("LORCANA_API_URL")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

class CardDataFetcher:
    def __init__(self):
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

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
            response = requests.get(f"{LORCANA_API_URL}/cards/{card_name}")
            response.raise_for_status()
            card_details = response.json()

            try:
                self.redis_client.set(card_name, json.dumps(card_details))
            except redis.exceptions.RedisError as e:
                print(f"Redis error: {e}")

            return card_details
        except requests.exceptions.RequestException as e:
            print(f"Error calling Lorcana API: {e}")
            return {}
