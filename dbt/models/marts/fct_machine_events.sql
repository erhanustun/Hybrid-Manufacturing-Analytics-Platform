select
    machine_id,
    event_type,

    count(*) as total_events,

    countif(event_type = 'ERROR') as error_events,

    min(event_time) as first_event_time,

    max(event_time) as last_event_time

from {{ ref('stg_machine_events') }}

group by
    machine_id,
    event_type