# Kafka Topics

- mfg.machine_events (CDC from public.machine_events)

## Key strategy
Key = machine_id
Reason: preserves ordering per machine and scales partitions safely.

