
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from validate_source import DATA_FILE, validate_source


def check_trip_durations():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    total_trips = 0
    zero_duration = 0
    negative_duration = 0
    over_24_hours = 0

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=[
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
        ],
    ):
        pickup = batch.column("tpep_pickup_datetime")
        dropoff = batch.column("tpep_dropoff_datetime")

        duration = pc.subtract(dropoff, pickup)

        zero = pc.equal(duration, pa.scalar(0, type=duration.type))
        negative = pc.less(duration, pa.scalar(0, type=duration.type))
        long_trip = pc.greater(
            duration,
            pa.scalar(
                24 * 60 * 60 * 1_000_000,
                type=pa.duration("us"),
            ),
        )

        total_trips += batch.num_rows
        zero_duration += pc.sum(pc.cast(zero, pa.int64())).as_py()
        negative_duration += pc.sum(
            pc.cast(negative, pa.int64())
        ).as_py()
        over_24_hours += pc.sum(
            pc.cast(long_trip, pa.int64())
        ).as_py()

    print("\nTrip duration quality check")
    print("---------------------------")
    print(f"Total trips checked: {total_trips:,}")
    print(f"Zero-duration trips: {zero_duration:,}")
    print(f"Negative-duration trips: {negative_duration:,}")
    print(f"Trips over 24 hours: {over_24_hours:,}")


if __name__ == "__main__":
    check_trip_durations()
