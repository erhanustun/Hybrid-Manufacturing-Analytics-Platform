# Day 5 – Change Data Capture (CDC) with Debezium

## Objective
Enable Change Data Capture (CDC) on PostgreSQL using Debezium in order to stream
row-level changes to Kafka in real time without polling.

---

## What Was Implemented

- PostgreSQL Write-Ahead Log (WAL) configured for **logical replication**
- Debezium PostgreSQL Connector deployed via **Kafka Connect**
- Replication slot and publication created for CDC
- Real-time CDC pipeline established from PostgreSQL to Kafka
- No polling mechanism used; changes are captured directly from WAL

---

## Kafka Integration

- Kafka used as the central event streaming platform
- Each INSERT/UPDATE/DELETE operation is emitted as an event
- Raw CDC events are published to the following topic:

---

## Validation

CDC functionality was validated by performing live INSERT operations on the
`machine_events` table and observing events appearing instantly in Kafka.

Example verification command:

docker exec -it infra-kafka-1 kafka-console-consumer \
  --bootstrap-server kafka:29092 \
  --topic mfg.public.machine_events
