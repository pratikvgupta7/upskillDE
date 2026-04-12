import duckdb
import os

RAW = '../data/raw/*.parquet'
CLEAN_DIR = '../data/clean/'

os.makedirs(CLEAN_DIR, exist_ok=True)

print("Writing cleaned data to Parquet...")

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

print("Done. Verifying output...")

duckdb.sql(f"""
    SELECT 
           pickup_month,
           count(*) AS total_trips,
           round(sum(fare_amount), 2) AS total_revenue
           FROM read_parquet('{CLEAN_DIR}/**/*.parquet')
           GROUP BY pickup_month
           ORDER BY pickup_month
           """).show()

duckdb.sql(f"""
    SELECT count(*) as total_rows,
           FROM read_parquet('{CLEAN_DIR}/**/*.parquet')
           """).show()