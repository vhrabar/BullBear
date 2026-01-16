from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass
class Settings:
    """
    Configuration settings for the scheduler service.
    """
    load_dotenv()
    MASSIVE_API_KEY: str = os.getenv("MASSIVE_API_KEY")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_PORT: str = os.getenv("DB_PORT")

    TEST_MODE: bool = os.getenv("TESTING", "false").lower() == "true"

    DJANGO_API_BASE_URL = "https://api.bull-bear.app"
    DJANGO_SERVICE_TOKEN = os.getenv("DJANGO_SERVICE_TOKEN")

    def __post_init__(self):
        self.DB_URL = (
            f"postgresql+psycopg2://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
