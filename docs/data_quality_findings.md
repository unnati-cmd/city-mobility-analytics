# Data Quality Findings

## Dataset

- **File:** `yellow_tripdata_2025-10.parquet`
- **Total records:** 4,428,699
- **Total columns:** 20
- **File format:** Parquet

## Findings

| Check | Finding | Records |
|---|---|---:|
| Missing values | Five columns each contain nulls | 990,887 per column |
| Missing-value relationship | All five fields are null together when `payment_type = 0` | 990,887 |
| Zero-duration trips | Pickup and drop-off timestamps are equal | 67,966 |
| Negative-duration trips | Drop-off precedes pickup | 2 |
| Long-duration trips | Duration exceeds 24 hours | 35 |
| Zero-distance trips | Recorded distance is zero | 125,599 |
| Negative-distance trips | Recorded distance is negative | 0 |
| Distance over 100 miles | Potentially unusual distance | 229 |
| Distance over 1,000 miles | Highly suspicious for ordinary NYC taxi trips | 149 |
| Negative fares | Potential adjustments or reversals | 321,307 |
| Zero fares | Recorded fare is zero | 2,076 |
| Fares over $500 | Potentially unusual fare | 53 |
| Fares over $1,000 | Potentially unusual fare | 2 |
| Zero passenger count | Passenger count is zero | 22,310 |
| Negative passenger count | Passenger count is negative | 0 |
| Passenger count over 6 | Requires review | 13 |

## Payment Type Distribution

| Payment type code | Records | Percentage |
|---:|---:|---:|
| 0 | 990,887 | 22.37% |
| 1 | 2,918,737 | 65.91% |
| 2 | 399,080 | 9.01% |
| 3 | 26,104 | 0.59% |
| 4 | 93,891 | 2.12% |

## Initial Handling Principles

1. Preserve the raw source data unchanged.
2. Preserve null values unless a justified business rule says otherwise.
3. Flag unusual records before deciding whether to exclude them.
4. Document every exclusion rule and report the number of excluded records.
5. Do not treat negative fares as invalid without investigating their meaning.
6. Verify code meanings against the official NYC TLC data dictionary.
7. Recheck the final quality counts after transformations.

## Status

Initial profiling is complete. Filtering thresholds and curated-data rules have not yet been finalized.