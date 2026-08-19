# Database Schema

## Entity relationships

```mermaid
erDiagram
  EQUIPMENT ||--o{ SENSOR_READINGS : produces
  SENSOR_READINGS ||--o| ANOMALY_RESULTS : receives
  EQUIPMENT ||--o{ MAINTENANCE_EVENTS : has

  EQUIPMENT {
    string id PK
    string name
    string equipment_type
    string location
    string protocol
    boolean active
  }
  SENSOR_READINGS {
    int id PK
    string equipment_id FK
    timestamp observed_at
    float temperature_c
    float vibration_mm_s
    float current_a
    float pressure_bar
    string operating_state
    string source_protocol
    string quality
  }
  ANOMALY_RESULTS {
    int id PK
    int reading_id FK
    string equipment_id
    timestamp scored_at
    float score
    boolean is_anomaly
    string model_version
    text explanation
  }
  MAINTENANCE_EVENTS {
    int id PK
    string equipment_id FK
    string event_type
    text description
    timestamp started_at
    timestamp completed_at
  }
```

`system_events` captures component events independently of equipment telemetry. The composite reading index on `(equipment_id, observed_at)` supports the dashboard's most common history query. Anomaly rows retain `equipment_id` in addition to the reading relationship to make event filtering explicit and efficient.

The MVP creates the initial schema at startup. Once the baseline stabilizes, add Alembic and require a migration for every schema change.

## Example reliability query

Daily anomalous-reading rate by equipment:

```sql
SELECT
    equipment_id,
    date_trunc('day', scored_at) AS day,
    count(*) FILTER (WHERE is_anomaly) AS anomaly_count,
    count(*) AS readings_scored,
    round(
        count(*) FILTER (WHERE is_anomaly)::numeric / nullif(count(*), 0),
        4
    ) AS anomaly_rate
FROM anomaly_results
GROUP BY equipment_id, date_trunc('day', scored_at)
ORDER BY day DESC, equipment_id;
```
