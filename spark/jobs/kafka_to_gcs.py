from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

spark = (
    SparkSession.builder
    .appName("kafka_to_gcs")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("event_id", LongType()),
    StructField("machine_id", IntegerType()),
    StructField("event_type", StringType()),
    StructField("event_time", StringType()),
    StructField("error_code", StringType()),
    StructField("payload", StringType()),
    StructField("cdc_op", StringType())
])

df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribe", "mfg.clean.machine_events")
    .load()
)

json_df = df.selectExpr("CAST(value AS STRING)")

parsed = json_df.select(
    from_json(col("value"), schema).alias("data")
).select("data.*")

query = (
    parsed.writeStream
    .format("parquet")
    .option("path", "gs://mfg-machine-events-erhan/machine_events/")
    .option("checkpointLocation", "/tmp/checkpoints/gcs_sink")
    .outputMode("append")
    .start()
)

query.awaitTermination()