
from pathlib import Path

# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the expected source file
DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "yellow_tripdata_2025-10.parquet"
)


def validate_source():
    if not DATA_FILE.exists():
        print(f"ERROR: Source file not found: {DATA_FILE}")
        return False

    file_size_mb = DATA_FILE.stat().st_size / (1024 * 1024)

    if file_size_mb == 0:
        print("ERROR: Source file is empty.")
        return False

    print("Source file validation successful!")
    print(f"File: {DATA_FILE.name}")
    print(f"Size: {file_size_mb:.2f} MB")

    return True


if __name__ == "__main__":
    import sys

    sys.exit(0 if validate_source() else 1)
