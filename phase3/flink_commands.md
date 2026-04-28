# Running the Flink SQL Job

## Prerequisites
Docker Compose stack running with Redpanda and Flink containers.

## Start Flink SQL Client
```bash
docker exec -it flink-jobmanager bash -c "bin/sql-client.sh \
  --jar /opt/flink/lib/custom/flink-sql-connector-kafka-3.1.0-1.18.jar \
  --jar /opt/flink/lib/custom/iceberg-flink-runtime-1.18-1.5.0.jar \
  --jar /opt/flink/lib/custom/bundle-2.20.18.jar"
```

## Run the job
```sql
-- paste contents of flink_interval_join.sql
```

## Monitor
- Flink UI: http://localhost:8081
- Redpanda Console: http://localhost:8080