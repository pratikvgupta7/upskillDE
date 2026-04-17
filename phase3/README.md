# Phase 3 — Streaming with Redpanda, Flink & Iceberg

Real-time taxi trip event streaming pipeline. A Python producer streams trip events from the cleaned dataset into a Redpanda (Kafka-compatible) topic; a Python consumer joins the events and writes completed trips to Parquet. The stack also includes Flink (for SQL-based stream processing) and an Iceberg REST catalog backed by MinIO.

## Architecture

```
data/clean/*.parquet
        │
        ▼
  producer.py  ──────►  Redpanda (topic: taxi-trips)
                                │
                                ▼
                        consumer.py
                         ┌──────────────────┐
                         │  join start+end  │
                         └──────────────────┘
                           │              │
                           ▼              ▼
               streaming_output/    streaming_orphans/
               batch_NNNNN.parquet  batch_NNNNN.parquet
```

## Services (docker-compose.yml)

| Service | Image | Port(s) | Role |
|---------|-------|---------|------|
| `redpanda` | redpandadata/redpanda | 9092 (internal), 9093 (external), 9644 | Kafka-compatible broker |
| `redpanda-console` | redpandadata/console | 8080 | Web UI for Redpanda |
| `flink-jobmanager` | custom (Dockerfile.flink) | 8081 | Flink job coordination |
| `flink-taskmanager` | custom (Dockerfile.flink) | — | Flink task execution |
| `minio` | minio/minio | 9000 (API), 9001 (console) | S3-compatible object store |
| `iceberg-rest` | tabulario/iceberg-rest | 8181 | Iceberg REST catalog pointing at MinIO |
| `spark-master` | apache/spark:3.5.1 | 8082, 7077 | Spark master (multi-engine query) |
| `spark-worker` | apache/spark:3.5.1 | — | Spark worker |
| `qdrant` | qdrant/qdrant | 6333, 6334 | Vector store (for phase 5) |

## Event model

The producer emits two events per trip on the `taxi-trips` topic, keyed by `trip_id` (UUID):

**trip_started**
```json
{
  "event_type": "trip_started",
  "trip_id": "<uuid>",
  "pickup_datetime": "...",
  "pickup_location_id": 123,
  "passenger_count": 1
}
```

**trip_ended**
```json
{
  "event_type": "trip_ended",
  "trip_id": "<uuid>",
  "dropoff_datetime": "...",
  "dropoff_location_id": 456,
  "fare_amount": 12.50,
  "tip_amount": 2.50,
  "payment_type": 1,
  "trip_distance": 3.2
}
```

The consumer joins these two events in memory by `trip_id` to produce a complete trip record.

## Scripts

### producer.py

Reads up to 10,000 trips from `data/clean/**/*.parquet` using DuckDB and streams them in a continuous loop to Redpanda at `localhost:9093`. Each trip becomes two Kafka messages (`trip_started` then `trip_ended`) with a 1 ms sleep between events to simulate real-time arrival.

```bash
pip install confluent-kafka duckdb
python phase3/producer.py
```

### consumer.py

Subscribes to `taxi-trips` from `localhost:9093`. Joins `trip_started` and `trip_ended` events by `trip_id` using an in-memory dictionary. Completed trips are flushed to Parquet in batches of 1,000.

- **Completed trips** → `data/streaming_output/batch_NNNNN.parquet`
- **Orphaned trip_ended events** (no matching start) → `data/streaming_orphans/batch_NNNNN.parquet`
- Health stats (completed, orphaned, unmatched starts) are printed every 5,000 messages.

```bash
pip install confluent-kafka polars
python phase3/consumer.py
```

## Running the full stack

```bash
# Start all services
cd phase3
docker compose up -d

# Wait for Redpanda to be ready, then in separate terminals:
python phase3/producer.py   # terminal 1
python phase3/consumer.py   # terminal 2
```

Redpanda Console is available at http://localhost:8080 to inspect the topic, consumer groups, and message lag.

Flink UI is at http://localhost:8081.

MinIO console is at http://localhost:9001 (user: `admin`, password: `password123`).

## Flink setup

The custom Flink image (`Dockerfile.flink`) extends `flink:1.18-scala_2.12-java11` and installs the Flink Shaded Hadoop uber JAR, which provides all Hadoop dependencies in a single artifact. Additional JARs are mounted at runtime from `./flink-jars/`:

- `flink-sql-connector-kafka-3.1.0-1.18.jar` — Flink ↔ Kafka/Redpanda connector
- `iceberg-flink-runtime-1.18-1.5.0.jar` — Iceberg sink for Flink
- Hadoop client JARs for S3/MinIO access

## Known limitations

- The consumer's in-memory join (`trip_started` dict) will grow unboundedly under high throughput or if producers restart without the consumer resetting its offset. In production this would be replaced by Flink stateful operators with a TTL.
- Orphans appear when the consumer starts mid-stream and `trip_ended` arrives before the corresponding `trip_started` has been seen.
- The Flink Iceberg integration was explored but writing a Flink SQL job that sinks directly into Iceberg on MinIO requires resolving JAR version conflicts between Hadoop, AWS SDK, and Iceberg runtimes — see the commit history for the attempted setup.
