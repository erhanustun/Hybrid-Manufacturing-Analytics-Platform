from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, get_json_object
from pyspark.sql.types import StructType, StructField, StringType

spark = (SparkSession.builder
         .appName("cdc_to_clean_topic")
         .getOrCreate())

spark.sparkContext.setLogLevel("WARN")

# Kafka'dan ham CDC mesajı oku
raw = (spark.readStream
       .format("kafka")
       .option("kafka.bootstrap.servers", "kafka:29092")
       .option("subscribe", "mfg.public.machine_events")
       .option("startingOffsets", "latest")
       .load())

# value binary -> string
raw_json = raw.selectExpr("CAST(value AS STRING) as json_str")

# Debezium JSON'undan after ve op alanını çekiyoruz (kolay yöntem: JSON path)
clean = raw_json.select(
    get_json_object(col("json_str"), "$.payload.after.event_id").cast("long").alias("event_id"),
    get_json_object(col("json_str"), "$.payload.after.machine_id").cast("long").alias("machine_id"),
    get_json_object(col("json_str"), "$.payload.after.event_type").alias("event_type"),
    get_json_object(col("json_str"), "$.payload.after.event_time").alias("event_time"),
    get_json_object(col("json_str"), "$.payload.after.error_code").alias("error_code"),
    get_json_object(col("json_str"), "$.payload.after.payload").alias("payload"),
    get_json_object(col("json_str"), "$.payload.op").alias("cdc_op")
)

# temiz event'i JSON'a çevirip yeni topic'e yaz
out = clean.selectExpr("to_json(struct(*)) AS value")

query = (out.writeStream
         .format("kafka")
         .option("kafka.bootstrap.servers", "kafka:29092")
         .option("topic", "mfg.clean.machine_events")
         .option("checkpointLocation", "/tmp/spark-checkpoints/cdc_to_clean_topic")
         .outputMode("append")
         .start())

query.awaitTermination()
