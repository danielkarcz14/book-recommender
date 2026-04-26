from pathlib import Path
from zipfile import ZipFile

import kaggle

from src.settings import DATASET
from src.settings import RAW_DATA_DIR


CSV_FILES = ("Books.csv", "Ratings.csv")
OUTPUT_DIR = RAW_DATA_DIR


def download_file(api, output_dir: Path, file_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / file_name

    if file_path.exists():
        print(f"{file_name} already exists, skipping download.")
        return file_path

    print(f"Downloading {file_name}...")
    api.dataset_download_file(DATASET, file_name=file_name, path=str(output_dir))

    zip_path = output_dir / f"{file_name}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Could not find archive {zip_path}.")

    with ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(output_dir)

    zip_path.unlink(missing_ok=True)

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find file {file_path} after extraction.")

    return file_path


def download_data(output_dir: str | Path = OUTPUT_DIR) -> list[Path]:
    kaggle.api.authenticate()

    output_path = Path(output_dir)
    downloaded_files = []

    for file_name in CSV_FILES:
        downloaded_files.append(download_file(kaggle.api, output_path, file_name))

    return downloaded_files


def check_if_exists(output_dir: str | Path = OUTPUT_DIR) -> list[Path]:
    output_path = Path(output_dir)
    existing_files = [output_path / file_name for file_name in CSV_FILES]

    if all(file_path.exists() for file_path in existing_files):
        print("All files already exist, skipping download.")
        return existing_files

    return download_data(output_path)


def main() -> int:
    try:
        check_if_exists()
    except Exception as exc:
        print(f"Failed to download dataset: {exc}")
        return 1

    print("Data are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
