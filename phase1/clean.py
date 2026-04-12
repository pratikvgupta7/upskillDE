import duckdb
import os
from pathlib import Path
import shutil

RAW = Path(__file__).parent.parent / 'data' / 'raw' / '*.parquet'
CLEAN_DIR = Path(__file__).parent.parent / 'data' / 'clean'

print("Writing cleaned data to Parquet...")
def run_cleaning():
    if CLEAN_DIR.exists():
        shutil.rmtree(CLEAN_DIR)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    duckdb.sql(f"""
        COPY (
            SELECT
                tpep_pickup_datetime                                        AS pickup_datetime,
                tpep_dropoff_datetime                                       AS dropoff_datetime,
                passenger_count,
                trip_distance,
                PULocationID                                                AS pickup_location_id,
                DOLocationID                                                AS dropoff_location_id,
                payment_type,
                fare_amount,
                tip_amount,
                tolls_amount,
                total_amount,
                -- derived columns
                round(tip_amount / fare_amount * 100, 2)                   AS tip_pct,
                epoch(tpep_dropoff_datetime - tpep_pickup_datetime) / 60   AS duration_minutes,
                hour(tpep_pickup_datetime)                                  AS pickup_hour,
                dayname(tpep_pickup_datetime)                               AS pickup_day,
                month(tpep_pickup_datetime)                                 AS pickup_month
            FROM read_parquet('{RAW}')
            WHERE fare_amount > 0
              AND trip_distance >= 0
              AND tpep_pickup_datetime <= tpep_dropoff_datetime
              AND payment_type BETWEEN 0 AND 6
              AND NOT (trip_distance = 0 AND fare_amount <= 0)
              AND month(tpep_pickup_datetime) IN (1,2)
        )
        TO '{CLEAN_DIR}'
        (FORMAT PARQUET, PARTITION_BY (pickup_month), OVERWRITE_OR_IGNORE TRUE)
    """)

    row_count = duckdb.sql(f"""
                           SELECT count(*) as clean_rows
                           FROM read_parquet('{CLEAN_DIR}/**/*.parquet')
                           """).fetchone()[0]
    return row_count

if __name__ == "__main__":
    clean_rows = run_cleaning()
    print(f"Cleaning complete. {clean_rows} rows written to {CLEAN_DIR}")