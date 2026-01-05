from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
