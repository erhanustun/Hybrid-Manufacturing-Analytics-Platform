# Hybrid Manufacturing Analytics Platform

> Real-time Change Data Capture (CDC) and streaming analytics pipeline for manufacturing systems

[![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow)](https://github.com/yourusername/hybrid-manufacturing-analytics-platform)
[![Days Completed](https://img.shields.io/badge/Progress-Day%206%2F90-blue)](./docs/)

---

## Overview
An end-to-end data engineering platform that captures transactional events from manufacturing systems in real time, processes them with streaming technologies, and delivers analytics-ready data for operational intelligence.

**Current capabilities:**
- ✅ PostgreSQL OLTP database with manufacturing schema
- ✅ Real-time CDC using Debezium (WAL-based, no polling)
- ✅ Kafka event streaming (raw + clean topics)
- ✅ Spark Structured Streaming for event transformation
- 🚧 Cloud storage layer (GCS + BigQuery) — in progress
- 🚧 dbt transformation models — planned
- 🚧 Airflow orchestration — planned

---

## Business Problem
Manufacturing systems generate high-frequency operational events (machine status, errors, quality metrics). Traditional batch ETL pipelines introduce latency, making real-time monitoring and anomaly detection difficult.

**This project demonstrates:**
- How to build a **low-latency streaming pipeline** using modern CDC and streaming tools
- How to transform **transactional data into analytics-ready events** in real time
- How to design a **hybrid (streaming + batch) data architecture** for manufacturing use cases

## Architecture
```
┌─────────────────┐
│   PostgreSQL    │  Manufacturing OLTP (machines, events, orders)
│    (OLTP DB)    │
└────────┬────────┘
         │ WAL-based CDC (Debezium)
         ↓
┌─────────────────┐
│   Kafka Broker  │  Raw CDC events (mfg.public.machine_events)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Spark Stream   │  Parse Debezium envelope → Clean JSON
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Kafka Topic   │  Clean events (mfg.clean.machine_events)
│    (Clean)      │
└────────┬────────┘
         │
         ↓
   [GCS → BigQuery → dbt]  ← Coming Next
```
---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Source** | PostgreSQL 16 |
| **CDC** | Debezium (PostgreSQL Connector) |
| **Streaming** | Apache Kafka 7.6 |
| **Processing** | Spark Structured Streaming 3.5.1 |
| **Orchestration** | Docker Compose |
| **Storage** | GCS + BigQuery *(planned)* |
| **Transformation** | dbt *(planned)* |
| **Workflow** | Apache Airflow *(planned)* |

---

## Data Source
PostgreSQL (Dockerized OLTP database) with simulated manufacturing events.

---

## Streaming Layer (Kafka + CDC)
Kafka is used as the central event streaming platform.
Debezium captures row-level changes from PostgreSQL using WAL-based CDC
and publishes them as events to Kafka topics.
This enables real-time propagation of manufacturing events across the platform.

---

## Processing Layer (Spark)
Spark Structured Streaming is used to consume CDC events from Kafka,
parse Debezium envelopes, transform raw events,
and publish analytics-ready data to clean Kafka topics.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB RAM minimum

### 1️⃣ Start Infrastructure
```bash
cd infra
docker compose up -d
```

**Services started:**
- PostgreSQL (`:5432`)
- Kafka (`:9092`)
- Zookeeper (`:2181`)
- Debezium Connect (`:8083`)
- Spark (`:8080`)

### 2️⃣ Create Debezium Connector
```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "manufacturing-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "debezium",
      "database.password": "debezium",
      "database.dbname": "manufacturing",
      "database.server.name": "mfg",
      "topic.prefix": "mfg",
      "table.include.list": "public.machine_events",
      "plugin.name": "pgoutput",
      "publication.name": "dbz_publication",
      "slot.name": "debezium_slot"
    }
  }'
```

### 3️⃣ Run Spark Streaming Job
```bash
docker exec -it infra-spark-1 spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /opt/spark-apps/jobs/cdc_to_clean_topic.py
```

### 4️⃣ Test the Pipeline
**Insert a test event:**
```bash
docker exec -it infra-postgres-1 psql -U de_user -d manufacturing -c "
INSERT INTO public.machine_events (machine_id, event_type, event_time, error_code, payload)
VALUES (1, 'ERROR', now(), 'E999', '{\"note\": \"TEST_EVENT\"}');
"
```

**Consume clean events:**
```bash
docker exec -it infra-kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic mfg.clean.machine_events
```

**Expected output:**
```json
{
  "event_id": 1234,
  "machine_id": 1,
  "event_type": "ERROR",
  "event_time": "2026-01-28T20:30:00Z",
  "error_code": "E999",
  "payload": "{\"note\": \"TEST_EVENT\"}",
  "cdc_op": "c"
}
```
---

## 📚 Documentation

Detailed daily engineering notes are available in the [`docs/`](./docs/) folder.

**Key documents:**
- [Day 5: CDC Setup with Debezium](./docs/day-05-cdc.md)
- [Day 6: Spark Streaming Transformation](./docs/day-06-spark-streaming.md)

---

## Use Cases
- Real-time monitoring of manufacturing events
- Event-driven analytics pipelines
- Streaming-based anomaly detection
- Near real-time data synchronization

---

## 🗓️ Roadmap

This project is being built in **7 phases over 90 days.**

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Infrastructure Skeleton & Architecture Design |
| **Phase 2** | ✅ Complete | Data Ingestion (CDC) & Streaming Foundation |
| **Phase 3** | 🚧 In Progress | Processing & Storage (Spark to BigQuery) |
| **Phase 4** | 📅 Planned | Analytics Layer (dbt Modeling) |
| **Phase 5** | 📅 Planned | Orchestration & Quality (Airflow) |
| **Phase 6** | 📅 Planned | Visualization & Storytelling |
| **Phase 7** | 📅 Planned | Final Optimization & Documentation |

---

**Status:** Day 6 of 90 completed 



