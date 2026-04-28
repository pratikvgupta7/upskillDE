-- Flink SQL — Interval Join Pipeline
-- Run inside Flink SQL client with Kafka and Iceberg JARs

-- Source table — reads from Kafka
CREATE TABLE taxi_events (
    event_type          STRING,
    trip_id             STRING,
    pickup_datetime     STRING,
    dropoff_datetime    STRING,
    pickup_location_id  INT,
    dropoff_location_id INT,
    passenger_count     INT,
    fare_amount         DOUBLE,
    tip_amount          DOUBLE,
    payment_type        INT,
    trip_distance       DOUBLE,
    proc_time           AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'taxi-trips',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'properties.group.id' = 'flink-processor',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
);

-- Sink table — print for development, replace with Iceberg for production
CREATE TABLE completed_trips (
    trip_id             STRING,
    pickup_datetime     STRING,
    dropoff_datetime    STRING,
    pickup_location_id  INT,
    dropoff_location_id INT,
    passenger_count     INT,
    fare_amount         DOUBLE,
    tip_amount          DOUBLE,
    payment_type        INT,
    trip_distance       DOUBLE
) WITH (
    'connector' = 'print'
);

-- Interval join — matches trip_started and trip_ended within 2 hour window
-- Bounded state — Flink discards unmatched events after 2 hours
INSERT INTO completed_trips
SELECT
    s.trip_id,
    s.pickup_datetime,
    e.dropoff_datetime,
    s.pickup_location_id,
    e.dropoff_location_id,
    s.passenger_count,
    e.fare_amount,
    e.tip_amount,
    e.payment_type,
    e.trip_distance
FROM taxi_events s
JOIN taxi_events e
    ON s.trip_id = e.trip_id
   AND s.event_type = 'trip_started'
   AND e.event_type = 'trip_ended'
   AND e.proc_time BETWEEN s.proc_time
       AND s.proc_time + INTERVAL '2' HOUR;