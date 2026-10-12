
import pyarrow.parquet as pq
from validate_source import DATA_FILE, validate_source


def profile_data():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    print("\nDataset data-quality profile")
    print("----------------------------")

    print("\nNull counts by column:")
    null_counts = {name: 0 for name in parquet_file.schema_arrow.names}

    for batch in parquet_file.iter_batches(batch_size=100_000):
        for name in null_counts:
            null_counts[name] += batch.column(name).null_count

    for name, count in null_counts.items():
        print(f"- {name}: {count:,}")

    print("\nProfiling complete.")


if __name__ == "__main__":
    profile_data()
