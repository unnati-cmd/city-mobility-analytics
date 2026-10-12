
import pyarrow.compute as pc
import pyarrow.parquet as pq

from validate_source import DATA_FILE, validate_source


def check_payment_types():
    if not validate_source():
        return

    parquet_file = pq.ParquetFile(DATA_FILE)
    payment_counts = {}

    for batch in parquet_file.iter_batches(
        batch_size=100_000,
        columns=["payment_type"],
    ):
        payment_column = batch.column("payment_type")
        counts = pc.value_counts(payment_column).to_pylist()

        for item in counts:
            value = item["values"]
            count = item["counts"]

            # Convert Arrow scalar values to ordinary Python values.
            if hasattr(value, "as_py"):
                value = value.as_py()

            payment_counts[value] = payment_counts.get(value, 0) + count

    print("\nPayment type distribution")
    print("--------------------------")

    for payment_type, count in sorted(
        payment_counts.items(),
        key=lambda item: (-1 if item[0] is None else item[0]),
    ):
        percentage = count * 100 / parquet_file.metadata.num_rows
        print(
            f"Payment type {payment_type}: "
            f"{count:,} trips ({percentage:.2f}%)"
        )


if __name__ == "__main__":
    check_payment_types()
