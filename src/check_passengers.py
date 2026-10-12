
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from validate_source import DATA_FILE, validate_source

def count_true(condition):
    result = pc.sum(pc.cast(condition, pa.int64())).as_py()
    return result if result is not None else 0


def check_passengers():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    total_trips = 0
    missing_passengers = 0
    zero_passengers = 0
    negative_passengers = 0
    over_6_passengers = 0
    maximum_passengers = None

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=["passenger_count"],
    ):
        passengers = batch.column("passenger_count")

        total_trips += batch.num_rows
        missing_passengers += passengers.null_count

        zero_passengers += count_true(pc.equal(passengers, 0))

        negative_passengers += count_true(pc.less(passengers, 0))

        over_6_passengers += count_true(pc.greater(passengers, 6))

        batch_max = pc.max(passengers).as_py()

        if batch_max is not None:
            maximum_passengers = (
                batch_max if maximum_passengers is None
                else max(maximum_passengers, batch_max)
            )

    print("\nPassenger count quality check")
    print("-----------------------------")
    print(f"Total trips checked: {total_trips:,}")
    print(f"Missing passenger counts: {missing_passengers:,}")
    print(f"Zero passenger counts: {zero_passengers:,}")
    print(f"Negative passenger counts: {negative_passengers:,}")
    print(f"Passenger counts over 6: {over_6_passengers:,}")
    print(f"Maximum recorded passenger count: {maximum_passengers}")


if __name__ == "__main__":
    check_passengers()
