import duckdb

# configure DuckDB to talk to MinIO
conn = duckdb.connect()
conn.execute("""
    INSTALL iceberg;
    LOAD iceberg;
    INSTALL httpfs;
    LOAD httpfs;
""")

conn.execute("""
    SET s3_endpoint='localhost:9000';
    SET s3_access_key_id='admin';
    SET s3_secret_access_key='password123';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
    SET unsafe_enable_version_guessing=true;
""")

print("=== Row count ===")
print(conn.execute("""
    SELECT count(*) AS total_rows
    FROM iceberg_scan('s3://warehouse/taxi/completed_trips')
""").fetchdf())

print("=== Revenue by payment type ===")
print(conn.execute("""
    SELECT
        payment_type,
        count(*)                        AS total_trips,
        round(sum(fare_amount), 2)      AS total_revenue,
        round(avg(fare_amount), 2)      AS avg_fare
    FROM iceberg_scan('s3://warehouse/taxi/completed_trips')
    GROUP BY payment_type
    ORDER BY total_trips DESC
""").fetchdf())

print("=== Top 5 pickup locations by trip count ===")
print(conn.execute("""
    SELECT
        pickup_location_id,
        count(*)                        AS total_trips,
        round(avg(fare_amount), 2)      AS avg_fare
    FROM iceberg_scan('s3://warehouse/taxi/completed_trips')
    GROUP BY pickup_location_id
    ORDER BY total_trips DESC
    LIMIT 5
""").fetchdf())