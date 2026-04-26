from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = REPO_ROOT / "config.ini"


def _load_config() -> ConfigParser:
    config = ConfigParser()
    loaded_files = config.read(CONFIG_FILE, encoding="utf-8")

    if not loaded_files:
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")

    return config


def _resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


config = _load_config()

DATASET = config["data"]["dataset"]
RAW_DATA_DIR = _resolve_repo_path(config["data"]["raw_data_dir"])
CLEANED_DATA_DIR = _resolve_repo_path(config["data"]["cleaned_data_dir"])

RAW_BOOKS_FILE = RAW_DATA_DIR / "Books.csv"
RAW_RATINGS_FILE = RAW_DATA_DIR / "Ratings.csv"

CLEANED_BOOKS_FILE = CLEANED_DATA_DIR / "books_cleaned.csv"
CLEANED_RATINGS_FILE = CLEANED_DATA_DIR / "ratings_cleaned.csv"

MIN_RATINGS = config.getint("model", "min_ratings")
DEFAULT_TOP_N = config.getint("app", "default_top_n")
