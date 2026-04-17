import duckdb
import pyarrow as pa
from pathlib import Path
from pyiceberg.catalog.rest import RestCatalog

CLEAN_DIR = Path(__file__).parent.parent / "data" / "clean"

# connect to catalog
catalog = RestCatalog(
    name="local",
    uri="http://localhost:8181",
    warehouse="s3://warehouse/",
    **{
        "s3.endpoint": "http://localhost:9000",
        "s3.access-key-id": "admin",
        "s3.secret-access-key": "password123",
        "s3.path-style-access": "true"
    }
)

# load the table
table = catalog.load_table("taxi.completed_trips")

# read January data from clean Parquet
print("Reading January data...")
jan_data = duckdb.sql(f"""
    SELECT
        gen_random_uuid()::VARCHAR      AS trip_id,
        pickup_datetime::VARCHAR        AS pickup_datetime,
        dropoff_datetime::VARCHAR       AS dropoff_datetime,
        pickup_location_id::INT         AS pickup_location_id,
        dropoff_location_id::INT        AS dropoff_location_id,
        passenger_count::INT            AS passenger_count,
        fare_amount::DOUBLE             AS fare_amount,
        tip_amount::DOUBLE              AS tip_amount,
        payment_type::INT               AS payment_type,
        trip_distance::DOUBLE           AS trip_distance
    FROM read_parquet('{CLEAN_DIR}/**/*.parquet')
    WHERE pickup_month = 1
    LIMIT 100000
""").arrow().read_all()

print(f"Writing {jan_data.num_rows} rows to Iceberg...")
table.append(jan_data)
print("January data written successfully")

# read February data
print("Reading February data...")
feb_data = duckdb.sql(f"""
    SELECT
        gen_random_uuid()::VARCHAR      AS trip_id,
        pickup_datetime::VARCHAR        AS pickup_datetime,
        dropoff_datetime::VARCHAR       AS dropoff_datetime,
        pickup_location_id::INT         AS pickup_location_id,
        dropoff_location_id::INT        AS dropoff_location_id,
        passenger_count::INT            AS passenger_count,
        fare_amount::DOUBLE             AS fare_amount,
        tip_amount::DOUBLE              AS tip_amount,
        payment_type::INT               AS payment_type,
        trip_distance::DOUBLE           AS trip_distance
    FROM read_parquet('{CLEAN_DIR}/**/*.parquet')
    WHERE pickup_month = 2
    LIMIT 100000
""").arrow().read_all()

print(f"Writing {feb_data.num_rows} rows to Iceberg...")
table.append(feb_data)
print("February data written successfully")

print("\n=== Verifying Iceberg table ===")
table = catalog.load_table("taxi.completed_trips")
df = table.scan().to_arrow()
print(f"Total rows: {df.num_rows}")
print(f"Schema: {df.schema}")