from pyiceberg.catalog.rest import RestCatalog

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

table = catalog.load_table("taxi.completed_trips")

# list all snapshots
print("=== Snapshots ===")
for snapshot in table.history():
    print(f"snapshot_id={snapshot.snapshot_id}  timestamp={snapshot.timestamp_ms}")

# read as of first snapshot — only January data
first_snapshot = table.history()[0].snapshot_id
print(f"\n=== Data as of first snapshot ({first_snapshot}) ===")
jan_only = table.scan(snapshot_id=first_snapshot).to_arrow()
print(f"Row count: {jan_only.num_rows}")
current = table.scan().to_arrow()
print(f"Current row count: {current.num_rows}")