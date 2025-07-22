from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    s3_bucket_name: str
    s3_region: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    lorcana_api_url: str
    database_url: str
    rabbitmq_host: str
    rabbitmq_queue: str
    testing: bool = False
    rabbitmq_url: str
    redis_host: str
    redis_port: int
    secret_key: str = "a_very_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
