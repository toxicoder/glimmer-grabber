import os
from unittest import TestCase
from unittest.mock import patch
from shared.config import Settings

class TestConfig(TestCase):
    @patch.dict(os.environ, {
        "DATABASE_URL": "test_db_url",
        "RABBITMQ_URL": "amqp://guest:guest@localhost:5672/",
        "S3_BUCKET_NAME": "test-bucket",
        "S3_REGION": "us-east-1",
        "MINIO_ENDPOINT": "http://localhost:9000",
        "MINIO_ACCESS_KEY": "minioadmin",
        "MINIO_SECRET_KEY": "minioadmin",
        "LORCANA_API_URL": "https://api.lorcana-api.com",
        "RABBITMQ_HOST": "localhost",
        "RABBITMQ_QUEUE": "lorcana_process_queue",
    })
    def test_settings(self):
        settings = Settings()
        self.assertEqual(settings.database_url, "test_db_url")
        self.assertEqual(settings.rabbitmq_url, "amqp://guest:guest@localhost:5672/")
        self.assertEqual(settings.s3_bucket_name, "test-bucket")
