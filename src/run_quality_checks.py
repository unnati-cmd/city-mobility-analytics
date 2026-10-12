
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from src.validate_source import DATA_FILE, validate_source

def count_true(condition):
    """Count true values while safely handling null results."""
    result = pc.sum(pc.cast(condition, pa.int64())).as_py()
    return result if result is not None else 0


def scalar_value(array, operation):
    """Return a numeric minimum or maximum from an Arrow array."""
    return getattr(pc, operation)(array).as_py()


def run_quality_checks():
    if not validate_source():
        raise SystemExit(1)

    parquet_file = pq.ParquetFile(DATA_FILE)
    total_rows = parquet_file.metadata.num_rows

    columns = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "payment_type",
        "RatecodeID",
        "store_and_fwd_flag",
        "congestion_surcharge",
        "Airport_fee",
    ]

    null_counts = {name: 0 for name in columns}

    metrics = {
        "zero_duration": 0,
        "negative_duration": 0,
        "over_24_hours": 0,
        "zero_distance": 0,
        "negative_distance": 0,
        "over_100_miles": 0,
        "over_1000_miles": 0,
        "negative_fares": 0,
        "zero_fares": 0,
        "fares_over_500": 0,
        "fares_over_1000": 0,
        "zero_passengers": 0,
        "negative_passengers": 0,
        "passengers_over_6": 0,
    }

    minimum_distance = None
    maximum_distance = None
    minimum_fare = None
    maximum_fare = None
    maximum_passengers = None
    payment_counts = {}

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=columns,
    ):
        for name in columns:
            null_counts[name] += batch.column(name).null_count

        pickup = batch.column("tpep_pickup_datetime")
        dropoff = batch.column("tpep_dropoff_datetime")
        duration = pc.subtract(dropoff, pickup)

        metrics["zero_duration"] += count_true(
            pc.equal(duration, pa.scalar(0, type=duration.type))
        )
        metrics["negative_duration"] += count_true(
            pc.less(duration, pa.scalar(0, type=duration.type))
        )
        metrics["over_24_hours"] += count_true(
            pc.greater(
                duration,
                pa.scalar(
                    24 * 60 * 60 * 1_000_000,
                    type=pa.duration("us"),
                ),
            )
        )

        distance = batch.column("trip_distance")

        metrics["zero_distance"] += count_true(
            pc.equal(distance, 0)
        )
        metrics["negative_distance"] += count_true(
            pc.less(distance, 0)
        )
        metrics["over_100_miles"] += count_true(
            pc.greater(distance, 100)
        )
        metrics["over_1000_miles"] += count_true(
            pc.greater(distance, 1000)
        )

        batch_min = scalar_value(distance, "min")
        batch_max = scalar_value(distance, "max")

        if batch_min is not None:
            minimum_distance = (
                batch_min if minimum_distance is None
                else min(minimum_distance, batch_min)
            )
        if batch_max is not None:
            maximum_distance = (
                batch_max if maximum_distance is None
                else max(maximum_distance, batch_max)
            )

        fare = batch.column("fare_amount")

        metrics["negative_fares"] += count_true(pc.less(fare, 0))
        metrics["zero_fares"] += count_true(pc.equal(fare, 0))
        metrics["fares_over_500"] += count_true(pc.greater(fare, 500))
        metrics["fares_over_1000"] += count_true(pc.greater(fare, 1000))

        batch_min = scalar_value(fare, "min")
        batch_max = scalar_value(fare, "max")

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

        passengers = batch.column("passenger_count")

        metrics["zero_passengers"] += count_true(
            pc.equal(passengers, 0)
        )
        metrics["negative_passengers"] += count_true(
            pc.less(passengers, 0)
        )
        metrics["passengers_over_6"] += count_true(
            pc.greater(passengers, 6)
        )

        batch_max = scalar_value(passengers, "max")
        if batch_max is not None:
            maximum_passengers = (
                batch_max if maximum_passengers is None
                else max(maximum_passengers, batch_max)
            )

        payment_values = pc.value_counts(
            batch.column("payment_type")
        ).to_pylist()

        for item in payment_values:
            value = item["values"]
            count = item["counts"]

            if hasattr(value, "as_py"):
                value = value.as_py()
            if hasattr(count, "as_py"):
                count = count.as_py()

            payment_counts[value] = payment_counts.get(value, 0) + count

    print("\nCITY MOBILITY — DATA QUALITY REPORT")
    print("=" * 42)
    print(f"Total records: {total_rows:,}")

    print("\nMissing values:")
    for name, count in null_counts.items():
        print(f"  {name}: {count:,}")

    print("\nTrip duration:")
    print(f"  Zero duration: {metrics['zero_duration']:,}")
    print(f"  Negative duration: {metrics['negative_duration']:,}")
    print(f"  Over 24 hours: {metrics['over_24_hours']:,}")

    print("\nTrip distance:")
    print(f"  Zero distance: {metrics['zero_distance']:,}")
    print(f"  Negative distance: {metrics['negative_distance']:,}")
    print(f"  Over 100 miles: {metrics['over_100_miles']:,}")
    print(f"  Over 1,000 miles: {metrics['over_1000_miles']:,}")
    print(f"  Minimum: {minimum_distance:,.2f} miles")
    print(f"  Maximum: {maximum_distance:,.2f} miles")

    print("\nFare amounts:")
    print(f"  Negative fares: {metrics['negative_fares']:,}")
    print(f"  Zero fares: {metrics['zero_fares']:,}")
    print(f"  Over $500: {metrics['fares_over_500']:,}")
    print(f"  Over $1,000: {metrics['fares_over_1000']:,}")
    print(f"  Minimum: ${minimum_fare:,.2f}")
    print(f"  Maximum: ${maximum_fare:,.2f}")

    print("\nPassenger counts:")
    print(f"  Missing: {null_counts['passenger_count']:,}")
    print(f"  Zero: {metrics['zero_passengers']:,}")
    print(f"  Negative: {metrics['negative_passengers']:,}")
    print(f"  Over 6: {metrics['passengers_over_6']:,}")
    print(f"  Maximum: {maximum_passengers}")

    print("\nPayment type distribution:")
    for payment_type in sorted(payment_counts):
        count = payment_counts[payment_type]
        percentage = count * 100 / total_rows
        print(
            f"  Type {payment_type}: {count:,} "
            f"({percentage:.2f}%)"
        )


    return {
        "total_rows": total_rows,
        "null_counts": null_counts,
        "metrics": metrics,
        "payment_counts": payment_counts,
        "minimum_distance": minimum_distance,
        "maximum_distance": maximum_distance,
        "minimum_fare": minimum_fare,
        "maximum_fare": maximum_fare,
        "maximum_passengers": maximum_passengers,
    }

if __name__ == "__main__":
    run_quality_checks()
