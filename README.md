# Hybrid Manufacturing Analytics Platform

## Overview
This project demonstrates an end-to-end hybrid data engineering pipeline
for manufacturing systems using simulated transactional and streaming data.

## Data Source
PostgreSQL (Dockerized OLTP database) with simulated manufacturing events.

## Current Status
- PostgreSQL running via Docker
- Schema applied (machines, products, production_orders, machine_events)
- Live event stream (~600 events/min) generated via Python

## Next Steps
- Define architecture and data flow
- Add CDC with Kafka (Debezium)
- Stream processing with Spark

## Business Problem
## Architecture
## Data Sources
## Streaming Layer (Kafka + CDC)
## Batch & Processing Layer (Spark)
## Storage (GCS + BigQuery)
## Transformation Layer (dbt)
## Orchestration (Airflow)
## Data Modeling
## Data Quality & Monitoring
## How to Run
## Future Improvements
