select
    event_id,
    machine_id,
    upper(event_type) as event_type,
    cast(event_time as timestamp) as event_time,
    error_code,
    payload,
    cdc_op
from {{ source('manufacturing', 'machine_events') }}