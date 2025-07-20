from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "a_very_secret_key"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
