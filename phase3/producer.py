import json
import time
import uuid
import duckdb
from pathlib import Path
from confluent_kafka import Producer

CLEAN_DIR = Path(__file__).parent.parent / "data" / "clean"
TOPIC = 'taxi-trips'

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")

producer = Producer({
    'bootstrap.servers': 'localhost:9093'
})

print("Loading trips...")
trips = duckdb.sql(f"""
    SELECT
        pickup_datetime::VARCHAR        AS pickup_datetime,
        dropoff_datetime::VARCHAR       AS dropoff_datetime,
        trip_distance,
        passenger_count,
        pickup_location_id,
        dropoff_location_id,
        payment_type,
        fare_amount,
        tip_amount,
        total_amount,
        pickup_hour,
        pickup_month
    FROM read_parquet('{CLEAN_DIR}/**/*.parquet')
    LIMIT 10000
""").fetchall()

columns = [
    'pickup_datetime', 'dropoff_datetime', 'trip_distance',
    'passenger_count', 'pickup_location_id', 'dropoff_location_id',
    'payment_type', 'fare_amount', 'tip_amount', 'total_amount',
    'pickup_hour', 'pickup_month'
]

print(f"Loaded {len(trips)} trips. Streaming continuously...")
loop = 0

while True:
    loop += 1
    print(f"Loop {loop} — streaming {len(trips)} trips...")

    for row in trips:
        trip = dict(zip(columns, row))
        trip_id = str(uuid.uuid4())

        # Event 1 — trip started
        trip_started = {
            "event_type": "trip_started",
            "trip_id": trip_id,
            "pickup_datetime": trip['pickup_datetime'],
            "pickup_location_id": trip['pickup_location_id'],
            "passenger_count": trip['passenger_count']
        }
        producer.produce(
            TOPIC,
            key=trip_id.encode('utf-8'), 
            value=json.dumps(trip_started).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)

        time.sleep(0.001)

        # Event 2 — trip ended
        trip_ended = {
            "event_type": "trip_ended",
            "trip_id": trip_id,
            "dropoff_datetime": trip['dropoff_datetime'],
            "dropoff_location_id": trip['dropoff_location_id'],
            "fare_amount": trip['fare_amount'],
            "tip_amount": trip['tip_amount'],
            "payment_type": trip['payment_type'],
            "trip_distance": trip['trip_distance']
        }
        producer.produce(
            TOPIC,
            
            value=json.dumps(trip_ended).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)

    producer.flush()
    print(f"Loop {loop} complete. Sleeping 5 seconds before next loop...")
    time.sleep(5)