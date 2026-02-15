# Day 6 – CDC to Spark Structured Streaming

## Objective
Build a real-time streaming pipeline that consumes Debezium CDC events from Kafka,
parses the Debezium envelope using Spark Structured Streaming,
and publishes cleaned events into a new Kafka topic.

---

## Starting Point
- PostgreSQL OLTP database running on Docker
- Debezium PostgreSQL connector already capturing WAL changes
- Raw CDC events available in Kafka topic:
  - `mfg.public.machine_events`

---

## Implementation

### Spark Streaming Job
- File: `spark/jobs/cdc_to_clean_topic.py`
- Reads from Kafka using Spark Structured Streaming
- Parses Debezium envelope using JSON path:
  - `$.payload.after.*`
- Filters invalid / tombstone messages
- Writes cleaned JSON events to:
  - `mfg.clean.machine_events`

---

## Running the Job

Running the Job
1) Listening to the Clean Topic

In a separate terminal, run:
docker exec -it infra-kafka-1 kafka-console-consumer  --bootstrap-server localhost:9092 --topic mfg.clean.machine_events  

Expected behavior:
The topic may be empty at first
It starts receiving messages as new events arrive
 
2) Starting the Spark Streaming Job
docker exec -it infra-spark-1 spark-submit  
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1  
/opt/spark-apps/jobs/cdc_to_clean_topic.py 
 
This job:
Reads events from the RAW topic
Parses Debezium CDC messages
Produces a clean JSON structure
Writes the transformed data to the CLEAN topic

3) Producing a Test Event
To trigger the pipeline, insert a test record into PostgreSQL:

docker exec -it infra-postgres-1 psql -U de_user -d manufacturing -c "
INSERT INTO public.machine_events (machine_id, event_type, event_time, error_code, payload)
VALUES (
  1,
  'ERROR',
  now(),
  'E999',
  '{\"note\": \"DAY6_TEST\", \"temp\": 111.1, \"severity\": \"HIGH\"}'
);