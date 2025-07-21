from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    S3_BUCKET_NAME: str
    S3_REGION: str
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    TESTING: bool = False
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_QUEUE: str = "test_queue"
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URL: str = "postgresql://user:password@postgres/database"
    LORCANA_API_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
