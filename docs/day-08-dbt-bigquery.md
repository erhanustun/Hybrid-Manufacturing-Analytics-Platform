# 📘 Day 8 - dbt Analytics Layer

## 🎯 Goal

Build the analytics layer on top of BigQuery using dbt.

Instead of querying the raw external table directly, introduce dbt models,
data quality tests, and layered transformations following modern Data Engineering practices.

---

## 🏗️ Architecture

```text
BigQuery External Table
            │
        source()
            │
            ▼
stg_machine_events
            │
          ref()
            │
            ▼
fct_machine_events
```

---

## ✅ Completed Tasks

- Configured dbt to connect to BigQuery
- Verified connection using `dbt debug`
- Created `sources.yml`
- Replaced hardcoded table references with `source()`
- Built the `stg_machine_events` staging model
- Added source-level data quality tests
- Executed `dbt run`
- Executed `dbt test`
- Built the first fact model (`fct_machine_events`)
- Connected models using `ref()`

---

## 📂 Models Created

### Source

```
manufacturing.machine_events
```

### Staging

```
stg_machine_events
```

Purpose:

- Standardize data
- Type conversion
- Prepare data for downstream models

### Fact

```
fct_machine_events
```

Contains:

- Total events
- Error events
- First event timestamp
- Last event timestamp

Aggregated by:

- machine_id
- event_type

---

## ✅ Validation

Verified in BigQuery:

- `machine_events`
- `stg_machine_events`
- `fct_machine_events`

Executed successfully:

```bash
docker compose exec dbt dbt debug
docker compose exec dbt dbt run
docker compose exec dbt dbt test
```

All models and tests completed successfully.

---

## 📚 Key Concepts Learned

- dbt Sources
- source()
- ref()
- Staging Layer
- Fact Layer
- schema.yml
- Data Quality Tests
- dbt Model Dependency

---

## 🚀 Result

The project now follows a layered analytics architecture:

```text
PostgreSQL
    ↓
Debezium
    ↓
Kafka
    ↓
Spark
    ↓
GCS
    ↓
BigQuery
    ↓
dbt Sources
    ↓
Staging Models
    ↓
Fact Models
```