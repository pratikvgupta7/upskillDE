from pyiceberg.catalog.rest import RestCatalog
import pyarrow as pa

# connect to the REST catalog
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

# create namespace
catalog.create_namespace_if_not_exists("taxi")

# define schema for completed trips
schema = pa.schema([
    pa.field("trip_id",             pa.string()),
    pa.field("pickup_datetime",     pa.string()),
    pa.field("dropoff_datetime",    pa.string()),
    pa.field("pickup_location_id",  pa.int32()),
    pa.field("dropoff_location_id", pa.int32()),
    pa.field("passenger_count",     pa.int32()),
    pa.field("fare_amount",         pa.float64()),
    pa.field("tip_amount",          pa.float64()),
    pa.field("payment_type",        pa.int32()),
    pa.field("trip_distance",       pa.float64()),
])

# create the table
catalog.create_table_if_not_exists(
    identifier="taxi.completed_trips",
    schema=schema
)

print("Table created successfully")
print(catalog.load_table("taxi.completed_trips").schema())