-- configure S3 and Iceberg
SET spark.hadoop.fs.s3a.endpoint=http://minio:9000;
SET spark.hadoop.fs.s3a.access.key=admin;
SET spark.hadoop.fs.s3a.secret.key=password123;
SET spark.hadoop.fs.s3a.path.style.access=true;
SET spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem;

-- row count
SELECT count(*) AS total_rows 
FROM iceberg.taxi.completed_trips;

-- revenue by payment type
SELECT
    payment_type,
    count(*)                    AS total_trips,
    round(sum(fare_amount), 2)  AS total_revenue,
    round(avg(fare_amount), 2)  AS avg_fare
FROM iceberg.taxi.completed_trips
GROUP BY payment_type
ORDER BY total_trips DESC;