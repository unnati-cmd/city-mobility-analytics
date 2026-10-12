
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from validate_source import DATA_FILE, validate_source


def check_trip_distances():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    total_trips = 0
    zero_distance = 0
    negative_distance = 0
    over_100_miles = 0
    over_1000_miles = 0
    maximum_distance = None

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=["trip_distance"],
    ):
        distance = batch.column("trip_distance")

        total_trips += batch.num_rows

        zero_distance += pc.sum(
            pc.cast(pc.equal(distance, 0), pa.int64())
        ).as_py()

        negative_distance += pc.sum(
            pc.cast(pc.less(distance, 0), pa.int64())
        ).as_py()

        over_100_miles += pc.sum(
            pc.cast(pc.greater(distance, 100), pa.int64())
        ).as_py()

        over_1000_miles += pc.sum(
            pc.cast(pc.greater(distance, 1000), pa.int64())
        ).as_py()

        batch_max = pc.max(distance).as_py()

        if batch_max is not None:
            if maximum_distance is None or batch_max > maximum_distance:
                maximum_distance = batch_max

    print("\nTrip distance quality check")
    print("---------------------------")
    print(f"Total trips checked: {total_trips:,}")
    print(f"Zero-distance trips: {zero_distance:,}")
    print(f"Negative-distance trips: {negative_distance:,}")
    print(f"Trips over 100 miles: {over_100_miles:,}")
    print(f"Trips over 1,000 miles: {over_1000_miles:,}")
    print(f"Maximum recorded distance: {maximum_distance:,.2f} miles")


if __name__ == "__main__":
    check_trip_distances()
