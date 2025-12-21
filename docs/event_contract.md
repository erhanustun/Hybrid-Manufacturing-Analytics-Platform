# Event Contract — machine_events

## Columns
event_id, machine_id, event_type, event_time, error_code, payload

## event_type
START | STOP | ERROR | HEARTBEAT

## payload by event_type

### START
{ "speed": 120 }

### STOP
{ "reason": "CHANGEOVER" }

### ERROR
{ "temp": 95.6, "severity": "MEDIUM" }

### HEARTBEAT
{ "vibration": 2.75, "amp": 17.05 }

## Notes
Kafka message key = machine_id (per-machine ordering).

