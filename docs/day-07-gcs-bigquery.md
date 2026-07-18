# Day 7 - Kafka to GCS and BigQuery

## Goal

Build an end-to-end streaming pipeline that delivers PostgreSQL CDC events to a cloud analytics platform.

The objective of Day 7 was to extend the existing CDC architecture beyond Kafka and persist streaming data into cloud storage and a query engine.

Final target:

```text
PostgreSQL
    ↓
Debezium CDC
    ↓
Kafka (Raw Topic)
    ↓
Spark Structured Streaming
    ↓
Kafka (Clean Topic)
    ↓
Spark Structured Streaming
    ↓
Google Cloud Storage (Parquet)
    ↓
BigQuery External Table
```

---

## Architecture
```text
PostgreSQL (OLTP)
        ↓
Debezium CDC
        ↓
Kafka Raw Topic
mfg.public.machine_events
        ↓
Spark Structured Streaming
cdc_to_clean_topic.py
        ↓
Kafka Clean Topic
mfg.clean.machine_events
        ↓
Spark Structured Streaming
kafka_to_gcs.py
        ↓
Google Cloud Storage (Parquet)
        ↓
BigQuery External Table
manufacturing.machine_events
```

---

## ☁️ GCP Setup

Created a dedicated Google Cloud project:

```text
manufacturing-analytics
```

Configured:

* Google Cloud Storage
* BigQuery
* Service Accounts
* IAM permissions

---

## GCS Bucket

Created a Cloud Storage bucket:

```text
mfg-machine-events-erhan
```

Directory structure:

```text
gs://mfg-machine-events-erhan/

├── machine_events/
├── checkpoints/
└── smoke_test/
```

Purpose:

* Store streaming data in Parquet format
* Persist Spark checkpoints
* Act as the project's Data Lake layer

---

## BigQuery Dataset

Created dataset:

```text
manufacturing
```

BigQuery is used as the analytics layer on top of Parquet files stored in GCS.

---

## Spark GCS Connector

Spark cannot communicate with Google Cloud Storage out of the box.

Added the GCS connector:

```text
gcs-connector-hadoop3-latest.jar
```

Verified connector availability:

```bash
docker exec -it infra-spark-1 ls /opt/bitnami/spark/jars | grep gcs
```

Result:

```text
gcs-connector-hadoop3-latest.jar
```

---

## Kafka to GCS Streaming Job

Created:

```text
spark/jobs/kafka_to_gcs.py
```

Responsibilities:

* Read events from:

```text
mfg.clean.machine_events
```

* Parse JSON payload
* Write records as Parquet files into:

```text
gs://mfg-machine-events-erhan/machine_events/
```

* Maintain checkpoint state

```text
gs://mfg-machine-events-erhan/checkpoints/
```

---

## BigQuery External Table

Created an External Table on top of GCS Parquet files.

```sql
CREATE EXTERNAL TABLE manufacturing.machine_events
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://mfg-machine-events-erhan/machine_events/*.parquet']
);
```

This allows BigQuery to query data directly from GCS without loading it into native BigQuery storage.

---

## Validation Tests

### Test 1 — PostgreSQL Insert

```sql
INSERT INTO machine_events
(machine_id,event_type,event_time,error_code,payload)
VALUES
(
  1,
  'ERROR',
  NOW(),
  'E999',
  '{"note":"DAY7_GCS_TEST_11"}'
);
```

---

### Test 2 — Kafka Raw Topic

Verified CDC event arrival:

```bash
docker exec -it infra-kafka-1 kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic mfg.public.machine_events
```

Observed:

```json
{
  "after": {
    "payload": "{\"note\":\"DAY7_GCS_TEST_11\"}"
  },
  "op": "c"
}
```

---

### Test 3 — Kafka Clean Topic

Verified Spark transformation:

```bash
docker exec -it infra-kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic mfg.clean.machine_events \
  --from-beginning
```

Observed:

```json
{
  "event_id": 9931,
  "machine_id": 1,
  "event_type": "ERROR",
  "payload": "{\"note\":\"DAY7_GCS_TEST_11\"}",
  "cdc_op": "c"
}
```

---

### Test 4 — BigQuery Query

```sql
SELECT *
FROM manufacturing.machine_events
LIMIT 10;
```

Successfully returned:

```text
DAY7_GCS_TEST_8
DAY7_GCS_TEST_9
DAY7_GCS_TEST_10
DAY7_GCS_TEST_11
```

---

## Key Learnings

### Debezium CDC Event Structure

Raw CDC events contain:

```text
before
after
source
op
timestamp
```

Operation types:

```text
c = INSERT
u = UPDATE
d = DELETE
```

---

### Raw Topic vs Clean Topic

Raw Topic:

```text
mfg.public.machine_events
```

Contains full CDC metadata.

Clean Topic:

```text
mfg.clean.machine_events
```

Contains analytics-ready events.

Benefits:

* Replay capability
* Easier debugging
* Better separation of concerns
* Cleaner downstream processing

---

### Kafka Offset vs Spark Checkpoint

Kafka Offset:

```text
Message position inside a Kafka topic
```

Spark Checkpoint:

```text
Latest successfully processed Kafka offset
```

Streaming jobs rely on checkpoint state to resume processing safely.

---

### Spark Connector Architecture

Spark acts as a processing engine and requires connectors for external systems.

| System         | Connector                |
| -------------- | ------------------------ |
| Kafka          | spark-sql-kafka          |
| GCS            | gcs-connector            |
| BigQuery       | spark-bigquery-connector |
| Delta Lake     | delta-core               |
| Apache Iceberg | iceberg-runtime          |

---

## Issues Encountered

### Missing Kafka Connector

Initial error:

```text
Failed to find data source: kafka
```

Cause:

```text
spark-sql-kafka connector was not available.
```

Solution:

```bash
spark-submit \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1
```

---

### GCS Sink Appeared Idle

At first, no new Parquet files appeared in GCS.

Root cause:

```text
cdc_to_clean_topic.py was not running,
therefore no new records were reaching
mfg.clean.machine_events.
```

Correct execution order:

```text
1. docker compose up -d
2. cdc_to_clean_topic.py
3. kafka_to_gcs.py
4. PostgreSQL INSERT
5. Validate outputs
```

---

## Final Result

Successfully built and validated an end-to-end streaming analytics pipeline:

```text
PostgreSQL
    ↓
Debezium CDC
    ↓
Kafka Raw Topic
    ↓
Spark Structured Streaming
    ↓
Kafka Clean Topic
    ↓
Spark Structured Streaming
    ↓
Google Cloud Storage (Parquet)
    ↓
BigQuery External Table
```

Final validation payload:

```text
DAY7_GCS_TEST_11
```

Pipeline Status:

```text
SUCCESS
```
