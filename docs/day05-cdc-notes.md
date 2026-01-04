### ✅ Day 5 – Change Data Capture (CDC) Enabled

- PostgreSQL WAL configured for logical replication
- Debezium Postgres Connector deployed via Kafka Connect
- Real-time CDC pipeline established from Postgres to Kafka
- Verified live INSERT events captured via WAL (no polling)
- Kafka topic: `mfg.public.machine_events`
