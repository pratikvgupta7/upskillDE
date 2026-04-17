# Phase 1 — Data Exploration & Cleaning

Exploratory analysis and cleaning of NYC Yellow Taxi trip data using DuckDB. Reads raw Parquet files, profiles data quality, and writes a partitioned clean dataset.

## What's here

| File | Purpose |
|------|---------|
| `explore.py` | Profile raw data: statistics, distributions, quality checks |
| `clean.py` | Apply cleaning rules and write partitioned Parquet output |

## Data

- **Input:** `data/raw/yellow_tripdata_2026-0{1,2}.parquet` — two months of raw NYC taxi trips
- **Output:** `data/clean/pickup_month={1,2}/*.parquet` — cleaned, partitioned by month

## What explore.py does

Runs a series of DuckDB queries against the raw files to understand the dataset before cleaning:

1. **Basic stats** — total trips, average distance/fare/tip, date range
2. **Schema** — column names and types
3. **Revenue by day of week** — which days generate the most revenue
4. **Busiest hours** — trip counts and average fare per hour
5. **Payment type breakdown** — revenue split across payment codes
6. **Tip distribution** — bucketed tip percentages (no tip / <10% / 10-20% / 20-30% / >30%)
7. **Data quality check** — counts of negative fares, zero distances, bad timestamps, zero passengers
8. **Zero-distance deep dive** — payment type and fare distribution for zero-distance rows
9. **Clean dataset preview** — row count and stats after applying all filters

## Cleaning rules (clean.py)

Rows are dropped if they fail any of these conditions:

| Rule | Reason |
|------|--------|
| `fare_amount > 0` | Zero/negative fares are invalid metered trips |
| `trip_distance >= 0` | Negative distances are corrupt |
| `pickup_datetime <= dropoff_datetime` | Dropoff before pickup is a timestamp error |
| `payment_type BETWEEN 0 AND 6` | Only known TLC payment codes are valid |
| `NOT (trip_distance = 0 AND fare_amount <= 0)` | Stationary zero-fare events are not trips |
| `month(pickup_datetime) IN (1, 2)` | Rows from other months are stale/mislabeled |

## Derived columns added by clean.py

| Column | Formula |
|--------|---------|
| `tip_pct` | `tip_amount / fare_amount * 100` |
| `duration_minutes` | `(dropoff_datetime - pickup_datetime)` in minutes |
| `pickup_hour` | Hour extracted from `pickup_datetime` |
| `pickup_day` | Day name (Monday, Tuesday, …) |
| `pickup_month` | Month number — also used as partition key |

## Running

```bash
# Profile the raw data
python phase1/explore.py

# Clean and write output
python phase1/clean.py
```

DuckDB is the only dependency — no database server required. Install with:

```bash
pip install duckdb
```

## Output layout

```
data/clean/
  pickup_month=1/
    *.parquet
  pickup_month=2/
    *.parquet
```

The clean Parquet files are consumed by Phase 2 (dbt + Dagster) as the source for all downstream models.
