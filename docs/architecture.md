# Architecture

## Goal

Demonstrate an end-to-end industrial telemetry path while keeping the project small enough to run on a laptop and explain in an interview.

## Components

| Component | Responsibility | Boundary |
|---|---|---|
| MQTT simulator | Publishes JSON telemetry for a pump and motor | Synthetic data only |
| Mosquitto | Routes MQTT messages | No durable message persistence in the demo |
| MQTT collector | Validates JSON and calls shared ingestion | Does not contain analytics rules |
| OPC-UA simulator | Exposes compressor values as address-space nodes | Not connected to a PLC |
| OPC-UA collector | Reads nodes and creates the normalized contract | Polling, not subscriptions |
| Ingestion service | Upserts equipment and transactionally stores reading + score | Shared by both protocols |
| Isolation Forest model | Produces a continuous score and anomaly flag | Trained on synthetic normal data |
| PostgreSQL | Persists operational and analytical records | Standard relational tables, not a specialized TSDB |
| FastAPI | Provides health and read APIs | Read-only in the MVP |
| Streamlit | Shows current values, trends, and anomaly events | Operator demo, not a production HMI |

## Data flow

1. Each simulator generates correlated temperature, vibration, current, and pressure values.
2. Fault windows increase bearing vibration or combine overheating, current rise, and pressure loss.
3. The protocol collector validates input with Pydantic and produces `TelemetryReading`.
4. The ingestion service creates the equipment record when first seen.
5. The scikit-learn pipeline scales the four features and computes an Isolation Forest decision score.
6. The reading and its anomaly result are committed together.
7. FastAPI queries the latest and historical records; Streamlit refreshes from those APIs.

## Failure behavior

- Collectors reconnect after broker or OPC-UA connection failures.
- Invalid MQTT payloads and invalid OPC-UA values are rejected and logged.
- Database connectivity is surfaced through `/health/ready`; process liveness remains separate.
- Collector database operations are transactional, so a reading is not committed without its score.
- Model artifacts are generated at container startup by the one-shot trainer.

## Scaling path

The MVP deliberately avoids pretending to be production-scale. A credible next step would partition readings by time, adopt schema migrations, add broker authentication/TLS, replace OPC-UA polling with subscriptions, separate online model serving, add idempotency keys, and instrument queue lag and inference latency. These should be justified by measured needs rather than added as résumé keywords.
