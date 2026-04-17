import json
import polars as pl
from pathlib import Path
from confluent_kafka import Consumer

TOPIC = 'taxi-trips'
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "streaming_output"
ORPHAN_DIR = Path(__file__).parent.parent / "data" / "streaming_orphans"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ORPHAN_DIR.mkdir(parents=True, exist_ok=True)

FLUSH_EVERY = 1000
ORPHAN_REPORT_EVERY = 5000  # report orphan count every N messages
batch_number = 0
orphan_batch_number = 0
message_count = 0

consumer = Consumer({
    'bootstrap.servers': 'localhost:9093',
    'group.id': 'taxi-processor',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe([TOPIC])

print("Consumer started. Waiting for messages...")

trip_started = {}
completed_trips = []
orphaned_ends = []      # trip_ended with no matching trip_started

def write_batch(trips, batch_num, output_dir, label):
    output_path = output_dir / f"batch_{batch_num:05d}.parquet"
    pl.DataFrame(trips).write_parquet(output_path)
    print(f"Written {label} batch {batch_num:05d} — "
          f"{len(trips)} trips → {output_path.name}")

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        message_count += 1
        event = json.loads(msg.value().decode('utf-8'))
        trip_id = event['trip_id']
        event_type = event['event_type']

        if event_type == 'trip_started':
            trip_started[trip_id] = event

        elif event_type == 'trip_ended':
            if trip_id in trip_started:
                start = trip_started.pop(trip_id)
                completed = {
                    'trip_id': trip_id,
                    'pickup_datetime': start['pickup_datetime'],
                    'dropoff_datetime': event['dropoff_datetime'],
                    'pickup_location_id': start['pickup_location_id'],
                    'dropoff_location_id': event['dropoff_location_id'],
                    'passenger_count': start['passenger_count'],
                    'fare_amount': event['fare_amount'],
                    'tip_amount': event['tip_amount'],
                    'payment_type': event['payment_type'],
                    'trip_distance': event['trip_distance']
                }
                completed_trips.append(completed)

                if len(completed_trips) >= FLUSH_EVERY:
                    batch_number += 1
                    write_batch(completed_trips, batch_number, OUTPUT_DIR, "completed")
                    completed_trips = []

            else:
                # trip_started never arrived — save as orphan
                orphaned_ends.append({
                    'trip_id': trip_id,
                    'dropoff_datetime': event['dropoff_datetime'],
                    'fare_amount': event['fare_amount'],
                    'tip_amount': event['tip_amount'],
                    'payment_type': event['payment_type'],
                    'trip_distance': event['trip_distance'],
                    'reason': 'missing_trip_started'
                })

                if len(orphaned_ends) >= FLUSH_EVERY:
                    orphan_batch_number += 1
                    write_batch(orphaned_ends, orphan_batch_number, ORPHAN_DIR, "orphan")
                    orphaned_ends = []

        # periodic health report
        if message_count % ORPHAN_REPORT_EVERY == 0:
            print(f"--- Health check at {message_count} messages ---")
            print(f"  Completed trips:        {batch_number * FLUSH_EVERY + len(completed_trips)}")
            print(f"  Orphaned trip_ends:     {orphan_batch_number * FLUSH_EVERY + len(orphaned_ends)}")
            print(f"  Unmatched trip_starts:  {len(trip_started)}")
            print(f"----------------------------------------------")

except KeyboardInterrupt:
    if completed_trips:
        batch_number += 1
        write_batch(completed_trips, batch_number, OUTPUT_DIR, "completed")
    if orphaned_ends:
        orphan_batch_number += 1
        write_batch(orphaned_ends, orphan_batch_number, ORPHAN_DIR, "orphan")
    print(f"\nShutdown. {batch_number} completed batches, "
          f"{orphan_batch_number} orphan batches.")

finally:
    consumer.close()