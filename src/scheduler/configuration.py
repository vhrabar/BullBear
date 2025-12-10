from dataclasses import dataclass
import os


@dataclass
class Settings:
    """
    Configuration settings for the scheduler service.
    """
    WEBSOCKET_URL: str = os.getenv("MASSIVE_WS_URL")
    DATABASE_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_PORT: str = os.getenv("DB_PORT")

    DB_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DATABASE_HOST}:{DB_PORT}/{DB_NAME}"
