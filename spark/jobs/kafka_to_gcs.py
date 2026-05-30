from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType

BUCKET_NAME = "mfg-machine-events-erhan"
OUTPUT_PATH = f"gs://{BUCKET_NAME}/machine_events/"
CHECKPOINT_PATH = f"gs://{BUCKET_NAME}/checkpoints/kafka_to_gcs/"

spark = (
    SparkSession.builder
    .appName("kafka_to_gcs")
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
    .config(
        "spark.hadoop.google.cloud.auth.service.account.json.keyfile",
        "/opt/gcp-credentials/service-account.json"
    )
    .config(
        "spark.hadoop.fs.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
    )
    .config(
        "spark.hadoop.fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("event_id", LongType(), True),
    StructField("machine_id", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("event_time", StringType(), True),
    StructField("error_code", StringType(), True),
    StructField("payload", StringType(), True),
    StructField("cdc_op", StringType(), True),
])

df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribe", "mfg.clean.machine_events")
    .option("startingOffsets", "latest")
    .load()
)

json_df = df.selectExpr("CAST(value AS STRING) AS value")

parsed = (
    json_df
    .select(from_json(col("value"), schema).alias("data"))
    .select("data.*")
    .where(col("event_id").isNotNull())
)

query = (
    parsed.writeStream
    .format("parquet")
    .option("path", OUTPUT_PATH)
    .option("checkpointLocation", CHECKPOINT_PATH)
    .outputMode("append")
    .start()
)

query.awaitTermination()