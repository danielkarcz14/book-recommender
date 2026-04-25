from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = REPO_ROOT / "data" / "raw"
CLEANED_DATA_DIR = REPO_ROOT / "data" / "cleaned"

RAW_BOOKS_FILE = RAW_DATA_DIR / "Books.csv"
RAW_RATINGS_FILE = RAW_DATA_DIR / "Ratings.csv"

CLEANED_BOOKS_FILE = CLEANED_DATA_DIR / "books_cleaned.csv"
CLEANED_RATINGS_FILE = CLEANED_DATA_DIR / "ratings_cleaned.csv"
