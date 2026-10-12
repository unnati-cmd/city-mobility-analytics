
import pyarrow.parquet as pq
from validate_source import DATA_FILE, validate_source


def inspect_data():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    print("\nDataset inspection")
    print("------------------")
    print(f"Total rows: {parquet_file.metadata.num_rows}")
    print(f"Total columns: {len(parquet_file.schema.names)}")

    print("\nColumn names and data types:")
    for field in parquet_file.schema_arrow:
        print(f"- {field.name}: {field.type}")


if __name__ == "__main__":
    inspect_data()
