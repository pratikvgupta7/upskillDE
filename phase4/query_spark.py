from pyspark.sql import SparkSession

# create Spark session with Iceberg and S3 support
spark = SparkSession.builder \
    .appName("IcebergQuery") \
    .master("spark://localhost:7077") \
    .config("spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
            "org.apache.hadoop:hadoop-aws:3.3.4,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.367") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg.type", "rest") \
    .config("spark.sql.catalog.iceberg.uri", "http://localhost:8181") \
    .config("spark.sql.catalog.iceberg.warehouse", "s3://warehouse/") \
    .config("spark.sql.catalog.iceberg.io-impl",
            "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.sql.catalog.iceberg.s3.endpoint", "http://localhost:9000") \
    .config("spark.sql.catalog.iceberg.s3.access-key-id", "admin") \
    .config("spark.sql.catalog.iceberg.s3.secret-access-key", "password123") \
    .config("spark.sql.catalog.iceberg.s3.path-style-access", "true") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=== Spark reading Iceberg table ===")

# query via Spark SQL using the catalog
df = spark.sql("SELECT * FROM iceberg.taxi.completed_trips")
df.printSchema()

print(f"Total rows: {df.count()}")

print("\n=== Revenue by payment type ===")
spark.sql("""
    SELECT
        payment_type,
        count(*)                        AS total_trips,
        round(sum(fare_amount), 2)      AS total_revenue,
        round(avg(fare_amount), 2)      AS avg_fare
    FROM iceberg.taxi.completed_trips
    GROUP BY payment_type
    ORDER BY total_trips DESC
""").show()

spark.stop()