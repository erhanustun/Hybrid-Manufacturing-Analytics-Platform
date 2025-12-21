# Hybrid Manufacturing Analytics Platform — Architecture

## Goal
Build an analytics-ready platform for manufacturing operations by capturing OLTP changes in near real-time (CDC),
processing events with a hybrid (stream + batch) approach, and delivering curated datasets for BI/analytics.

## High-level flow
1) PostgreSQL (OLTP) stores transactional production data and machine events.
2) Debezium (CDC) captures changes and publishes them to Kafka topics.
3) Spark Structured Streaming consumes Kafka topics and standardizes events.
4) Curated data is written to GCS (Parquet).
5) BigQuery queries curated datasets.
6) dbt builds staging → marts.
7) Airflow orchestrates batch jobs and quality checks.

## Diagram
```mermaid
flowchart LR
  A[(PostgreSQL\nOLTP)] -->|CDC (Debezium)| B[(Kafka)]
  B -->|Structured Streaming| C[Spark]
  C -->|Parquet| D[(GCS)]
  D --> E[(BigQuery)]
  E --> F[dbt]
  F --> G[BI]

  H[Airflow] -.-> B
  H -.-> C
  H -.-> F

