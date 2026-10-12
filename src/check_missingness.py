
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from validate_source import DATA_FILE, validate_source


def check_missingness():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)

    columns = [
        "passenger_count",
        "RatecodeID",
        "store_and_fwd_flag",
        "congestion_surcharge",
        "Airport_fee",
    ]

    payment_zero_count = 0
    all_five_null_count = 0
    all_five_null_and_payment_zero = 0

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=columns + ["payment_type"],
    ):
        payment_zero = pc.equal(batch.column("payment_type"), 0)

        all_null = pc.is_null(batch.column(columns[0]))

        for column in columns[1:]:
            all_null = pc.and_(
                all_null,
                pc.is_null(batch.column(column)),
            )

        payment_zero_count += pc.sum(
            pc.cast(payment_zero, pa.int64())
        ).as_py()

        all_five_null_count += pc.sum(
            pc.cast(all_null, pa.int64())
        ).as_py()

        both_conditions = pc.and_(all_null, payment_zero)

        all_five_null_and_payment_zero += pc.sum(
            pc.cast(both_conditions, pa.int64())
        ).as_py()

    print("\nMissing-value relationship check")
    print("--------------------------------")
    print(f"Records with payment_type = 0: {payment_zero_count:,}")
    print(f"Records with all five fields null: {all_five_null_count:,}")
    print(
        "Records with all five fields null AND payment_type = 0: "
        f"{all_five_null_and_payment_zero:,}"
    )


if __name__ == "__main__":
    check_missingness()
