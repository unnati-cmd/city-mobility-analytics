
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from validate_source import DATA_FILE, validate_source


def check_fares():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    total_trips = 0
    negative_fares = 0
    zero_fares = 0
    over_500 = 0
    over_1000 = 0
    maximum_fare = None
    minimum_fare = None

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=["fare_amount"],
    ):
        fare = batch.column("fare_amount")

        total_trips += batch.num_rows

        negative_fares += pc.sum(
            pc.cast(pc.less(fare, 0), pa.int64())
        ).as_py()

        zero_fares += pc.sum(
            pc.cast(pc.equal(fare, 0), pa.int64())
        ).as_py()

        over_500 += pc.sum(
            pc.cast(pc.greater(fare, 500), pa.int64())
        ).as_py()

        over_1000 += pc.sum(
            pc.cast(pc.greater(fare, 1000), pa.int64())
        ).as_py()

        batch_min = pc.min(fare).as_py()
        batch_max = pc.max(fare).as_py()

        if batch_min is not None:
            minimum_fare = (
                batch_min if minimum_fare is None
                else min(minimum_fare, batch_min)
            )

        if batch_max is not None:
            maximum_fare = (
                batch_max if maximum_fare is None
                else max(maximum_fare, batch_max)
            )

    print("\nFare amount quality check")
    print("-------------------------")
    print(f"Total trips checked: {total_trips:,}")
    print(f"Negative fares: {negative_fares:,}")
    print(f"Zero fares: {zero_fares:,}")
    print(f"Fares over $500: {over_500:,}")
    print(f"Fares over $1,000: {over_1000:,}")
    print(f"Minimum fare: ${minimum_fare:,.2f}")
    print(f"Maximum fare: ${maximum_fare:,.2f}")


if __name__ == "__main__":
    check_fares()
