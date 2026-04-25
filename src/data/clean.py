import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.download import check_if_exists


RAW_DATA_DIR = REPO_ROOT / "data" / "raw"
CLEANED_DATA_DIR = REPO_ROOT / "data" / "cleaned"
RAW_BOOKS_FILE = RAW_DATA_DIR / "Books.csv"
RAW_RATINGS_FILE = RAW_DATA_DIR / "Ratings.csv"
CLEANED_BOOKS_FILE = CLEANED_DATA_DIR / "books_cleaned.csv"
CLEANED_RATINGS_FILE = CLEANED_DATA_DIR / "ratings_cleaned.csv"


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    check_if_exists(RAW_DATA_DIR)

    books = pd.read_csv(
        RAW_BOOKS_FILE,
        dtype={"ISBN": str},
        on_bad_lines="skip",
        low_memory=False,
    )
    ratings = pd.read_csv(
        RAW_RATINGS_FILE,
        dtype={"ISBN": str},
        on_bad_lines="skip",
        low_memory=False,
    )

    return books, ratings


def clean_books(books: pd.DataFrame) -> pd.DataFrame:
    cleaned = books.copy()

    cleaned = cleaned.drop(columns=["Image-URL-S", "Image-URL-M", "Image-URL-L"], errors="ignore")
    cleaned = cleaned.dropna(subset=["ISBN", "Book-Title", "Book-Author", "Publisher"])
    cleaned = cleaned.drop_duplicates(subset=["ISBN"])

    cleaned["Year-Of-Publication"] = pd.to_numeric(cleaned["Year-Of-Publication"], errors="coerce")
    cleaned = cleaned[
        cleaned["Year-Of-Publication"].isna()
        | ((cleaned["Year-Of-Publication"] >= 1500) & (cleaned["Year-Of-Publication"] <= 2025))
    ]

    for column in ["ISBN", "Book-Title", "Book-Author", "Publisher"]:
        cleaned[column] = cleaned[column].astype(str).str.strip()

    return cleaned


def clean_ratings(ratings: pd.DataFrame, valid_isbns: set[str]) -> pd.DataFrame:
    cleaned = ratings.copy()

    cleaned = cleaned.dropna(subset=["User-ID", "ISBN", "Book-Rating"])
    cleaned["Book-Rating"] = pd.to_numeric(cleaned["Book-Rating"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Book-Rating"])
    cleaned = cleaned[cleaned["Book-Rating"] != 0]
    cleaned["ISBN"] = cleaned["ISBN"].astype(str).str.strip()
    cleaned = cleaned[cleaned["ISBN"].isin(valid_isbns)]
    cleaned = cleaned.drop_duplicates(subset=["User-ID", "ISBN"])

    return cleaned


def build_cleaned_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    books, ratings = load_raw_data()
    books_cleaned = clean_books(books)
    ratings_cleaned = clean_ratings(ratings, set(books_cleaned["ISBN"]))

    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    books_cleaned.to_csv(CLEANED_BOOKS_FILE, index=False)
    ratings_cleaned.to_csv(CLEANED_RATINGS_FILE, index=False)

    return books_cleaned, ratings_cleaned


def main() -> int:
    try:
        print("Nacitam raw data...")
        books, ratings = load_raw_data()
        print(f"Raw books: {len(books)}")
        print(f"Raw ratings: {len(ratings)}")

        print("Cistim books...")
        books_cleaned = clean_books(books)
        print(f"Cleaned books: {len(books_cleaned)}")

        print("Cistim ratings...")
        ratings_cleaned = clean_ratings(ratings, set(books_cleaned["ISBN"]))
        print(f"Cleaned ratings: {len(ratings_cleaned)}")

        CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        books_cleaned.to_csv(CLEANED_BOOKS_FILE, index=False)
        ratings_cleaned.to_csv(CLEANED_RATINGS_FILE, index=False)
    except Exception as exc:
        print(f"Cisteni dat selhalo: {exc}")
        return 1

    print("Vycistena data jsou ulozena v data/cleaned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
