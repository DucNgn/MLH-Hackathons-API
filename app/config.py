from functools import lru_cache
from pathlib import Path

from pydantic import BaseConfig


class Settings(BaseConfig):
    TIMEZONE = "America/Toronto"
    MLH_EVENT_PARSER = "html.parser"
    MLH_EVENT_STORAGE = "./data"
    MLH_EVENT_STORAGE_FOLDER_PATH = (
        Path(__file__).parent.resolve() / MLH_EVENT_STORAGE
    )  # noqa
    MLH_EVENT_STORAGE_FILE_PATH = MLH_EVENT_STORAGE_FOLDER_PATH / "events.json"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
