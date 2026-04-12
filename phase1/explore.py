import duckdb
import time

# point to raw files
RAW = "../data/raw/"

# Basic stats
print("=== ROW COUNT & BASIC STATS ===")

duckdb.sql(f"""
           SELECT 
                count(*)                          AS total_trips,
                round(avg(trip_distance), 2)      AS avg_distance_miles,
                round(avg(fare_amount), 2)        AS avg_fare,
                round(avg(tip_amount), 2)         AS avg_tip,
                min(tpep_pickup_datetime)         AS earliest_trip,
                max(tpep_pickup_datetime)         AS latest_trip
            FROM read_parquet('{RAW}')
           """).show()

# What columns do we have?
print("\n=== SCHEMA ===")
duckdb.sql(f"DESCRIBE SELECT * FROM read_parquet('{RAW}')").show()

start = time.time()
duckdb.sql(f"SELECT COUNT(*) AS totalRows FROM read_parquet('{RAW}')").show()
elapsed = time.time() - start
print(f"\n ==== COUNTING ROW TOOK {elapsed:.3f} seconds ====)")

# 1. Revenue by day of week
print("=== REVENUE BY DAY OF WEEK ===")
duckdb.sql(f"""
        SELECT 
           dayname(tpep_pickup_datetime) AS day_of_week,
           count(*) AS total_trips,
           round(sum(fare_amount), 2) AS total_revenue,
              round(avg(fare_amount), 2) AS avg_fare
           FROM read_parquet('{RAW}')
           GROUP BY dayname(tpep_pickup_datetime)
           ORDER BY total_revenue DESC
           """).show()

# 2. Busiest pickup hours
print("=== BUSIEST HOURS ===")
duckdb.sql(f"""
        SELECT 
              hour(tpep_pickup_datetime) AS pickup_hour,
                count(*) AS total_trips,
                round(avg(fare_amount), 2) AS avg_fare
            FROM read_parquet('{RAW}')
            WHERE fare_amount > 0
            GROUP BY hour(tpep_pickup_datetime)
            ORDER BY total_trips DESC
           """).show()

# 3. Payment type breakdown
print("=== PAYMENT TYPES ===")
duckdb.sql(f"""
           SELECT 
              payment_type,
                count(*) AS total_trips,
                round(sum(fare_amount), 2) AS total_revenue
            FROM read_parquet('{RAW}')
            GROUP BY payment_type
            ORDER BY total_revenue DESC
           """).show()

# 4. Tip percentage distribution
print("=== TIP DISTRIBUTION ===")
duckdb.sql(f"""
        SELECT 
        CASE 
            WHEN tip_amount = 0              THEN 'No tip'
            WHEN tip_amount / fare_amount < 0.10 THEN 'Under 10%'
            WHEN tip_amount / fare_amount < 0.20 THEN '10-20%'
            WHEN tip_amount / fare_amount < 0.30 THEN '20-30%'
            ELSE 'Over 30%'
        END                               AS tip_bucket,
        count(*)                          AS total_trips,
        round(count(*) * 100.0 / sum(count(*)) OVER (), 2) AS pct_of_trips
        FROM read_parquet('{RAW}')
        WHERE fare_amount > 0 AND tip_amount >= 0
        GROUP BY tip_bucket
        ORDER BY total_trips DESC
           """).show()

# 5. Data quality check - how dirty is this data?
print("=== DATA QUALITY ===")
duckdb.sql(f"""
    SELECT
        count(*)                                        AS total_rows,
        count(*) FILTER (WHERE fare_amount <= 0)        AS negative_or_zero_fare,
        count(*) FILTER (WHERE trip_distance = 0)       AS zero_distance,
        count(*) FILTER (WHERE tpep_pickup_datetime 
            > tpep_dropoff_datetime)                    AS dropoff_before_pickup,
        count(*) FILTER (WHERE passenger_count = 0)     AS zero_passengers
    FROM read_parquet('{RAW}')
""").show()


print("=== ZERO DISTANCE DEEP DIVE ===")
duckdb.sql(f"""
    SELECT
        payment_type,
        round(avg(fare_amount), 2)      AS avg_fare,
        round(avg(tip_amount), 2)       AS avg_tip,
        count(*)                        AS trip_count
    FROM read_parquet('{RAW}')
    WHERE trip_distance = 0
      AND fare_amount > 0
    GROUP BY payment_type
    ORDER BY trip_count DESC
""").show()

print("=== ZERO DISTANCE FARE DISTRIBUTION ===")
duckdb.sql(f"""
    SELECT
        CASE
            WHEN fare_amount <= 0   THEN 'zero/negative'
            WHEN fare_amount < 5    THEN 'under $5'
            WHEN fare_amount < 20   THEN '$5-$20'
            ELSE 'over $20'
        END                             AS fare_bucket,
        count(*)                        AS trip_count
    FROM read_parquet('{RAW}')
    WHERE trip_distance = 0
    GROUP BY fare_bucket
    ORDER BY trip_count DESC
""").show()

print("=== CLEAN DATASET PREVIEW ===")
duckdb.sql(f"""
    SELECT
        count(*)                        AS clean_rows,
        round(avg(fare_amount), 2)      AS avg_fare,
        round(avg(trip_distance), 2)    AS avg_distance
    FROM read_parquet('{RAW}')
    WHERE fare_amount > 0
      AND trip_distance >= 0
      AND tpep_pickup_datetime <= tpep_dropoff_datetime
      AND payment_type BETWEEN 1 AND 4
      AND NOT (trip_distance = 0 AND fare_amount <= 0)
""").show()