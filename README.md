# Hybrid Manufacturing Analytics Platform

## Overview
This project demonstrates an end-to-end hybrid data engineering pipeline
for manufacturing systems using simulated transactional and streaming data.

## Data Source
PostgreSQL (Dockerized OLTP database) with simulated manufacturing events.

## Current Status
- PostgreSQL running via Docker with OLTP schema applied
- Simulated manufacturing events ingested into `machine_events`
- Kafka and Zookeeper running via Docker
- Debezium Postgres Connector enabled for Change Data Capture (CDC)
- Real-time CDC pipeline from PostgreSQL WAL to Kafka
- Kafka topic: `mfg.public.machine_events`
- Live CDC verified with INSERT events (no polling)

## Next Steps
- Define detailed system architecture and data flow
- Transform raw CDC events into analytics-ready events using Spark
- Persist streaming data to cloud storage (GCS / BigQuery)
- Build transformation layer with dbt

## Business Problem
## Architecture
## Data Sources
## Streaming Layer (Kafka + CDC)
- Kafka used as the central event streaming platform
- Debezium captures row-level changes from PostgreSQL using WAL
- Each INSERT/UPDATE/DELETE is published as an event to Kafka
- Enables real-time propagation of manufacturing events
## Batch & Processing Layer (Spark)
## Storage (GCS + BigQuery)
## Transformation Layer (dbt)
## Orchestration (Airflow)
## Data Modeling
## Data Quality & Monitoring
## How to Run
## Future Improvements
