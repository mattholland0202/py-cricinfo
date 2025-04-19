from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


def _load_version() -> str:
    base_path = Path(__file__).parent.parent
    file_path = (base_path / "version.txt").resolve()
    with open(file_path, "r") as file:
        version = file.readline()
    return version


class Settings(BaseSettings):
    APP_VERSION: str = _load_version()


@lru_cache
def get_settings():
    return Settings()