# Day 9 - dbt Testing, Documentation and Lineage

## Goal

The goal of Day 9 was to improve the reliability and maintainability of the analytics layer by adding data quality tests, documentation, and lineage visualization with dbt.

By the end of this day, the dbt project was able to:

- Validate data quality using automated tests
- Document models and columns
- Generate interactive dbt documentation
- Visualize dependencies between source, staging, and fact models

---

## Analytics Architecture

The dbt analytics layer currently follows this structure:

```text
BigQuery External Table
manufacturing.machine_events
        │
        ▼
dbt Source
        │
        ▼
stg_machine_events
        │
        ▼
fct_machine_events


This dependency chain is automatically detected by dbt through source() and ref().

🧪 Data Quality Tests

Data quality tests were added to the dbt models.

Examples include:

not_null
unique

For example, event_id in the staging model is expected to be both present and unique.

columns:
  - name: event_id
    tests:
      - not_null
      - unique

Other important columns such as machine_id, event_type, and total_events were also validated.

Tests were executed using:

docker compose exec dbt dbt test

Result:

PASS=8
WARN=0
ERROR=0
SKIP=0
TOTAL=8

All 8 data quality tests passed successfully.

📚 Model Documentation

Descriptions were added to dbt models and their columns using YAML configuration files.

For example, the fct_machine_events model was documented as an aggregated analytics model containing machine event metrics.

Column descriptions were also added for fields such as:

machine_id
event_type
total_events
error_events
first_event_time
last_event_time

This documentation allows engineers and analysts to understand the purpose of the models without reading the SQL implementation directly.

⚙️ Generate dbt Documentation

dbt documentation was generated using:

docker compose exec dbt dbt docs generate

This command analyzes the dbt project and generates documentation artifacts inside the target/ directory.

Important generated files include:

target/
├── catalog.json
├── manifest.json
└── index.html

These files contain information about:

Models
Sources
Columns
Tests
Dependencies
Database metadata
Lineage relationships
🌐 Serve dbt Documentation

The generated documentation was served using:

dbt docs serve

The dbt container was configured so the documentation interface could be accessed from the host machine.

The documentation UI was available at:

http://localhost:8081

Through the dbt Docs interface, models, columns, SQL code, tests, sources, and dependencies can be explored interactively.

🔗 Data Lineage

One of the most important results of Day 9 was generating the dbt lineage graph.

The lineage graph showed:

manufacturing.machine_events
          │
          ▼
stg_machine_events
          │
          ▼
fct_machine_events

This represents the complete transformation path of the analytics layer.

Source
manufacturing.machine_events

The BigQuery external table containing machine event data written to GCS by Spark.

Staging
stg_machine_events

The dbt staging model responsible for cleaning and preparing the source data.

Mart / Fact Model
fct_machine_events

The analytics model containing aggregated machine event metrics.

dbt automatically understands these relationships through:

{{ source('manufacturing', 'machine_events') }}

and:

{{ ref('stg_machine_events') }}
🔍 What We Learned

Day 9 introduced several important analytics engineering concepts:

Data Testing

Data pipelines should not only move data.

They should also validate that the data satisfies expected quality rules.

Documentation

dbt allows documentation to live directly next to the transformation code.

This makes the analytics layer easier to understand and maintain.

Data Lineage

Lineage makes it possible to understand where data comes from and how models depend on each other.

Instead of manually drawing dependencies, dbt automatically builds the dependency graph using source() and ref().

Analytics Engineering

At this point, the project is no longer only a streaming pipeline.

It now contains a structured analytics layer with:

Source
   ↓
Staging
   ↓
Fact Model
   ↓
Tests
   ↓
Documentation
   ↓
Lineage
✅ Final Result

Day 9 successfully completed the dbt analytics engineering foundation.

The project now includes:

✅ dbt source definitions
✅ Staging model
✅ Fact model
✅ Automated data quality tests
✅ Model documentation
✅ Column documentation
✅ Interactive dbt Docs
✅ Data lineage visualization
✅ 8/8 passing tests

The analytics layer is now tested, documented, and easier to maintain.