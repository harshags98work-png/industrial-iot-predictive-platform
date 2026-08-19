# Completion Plan

## Phase 1 — Working vertical slice (complete)

- [x] Define the normalized telemetry contract.
- [x] Simulate normal and faulted MQTT equipment.
- [x] Store equipment, readings, and anomaly results.
- [x] Expose health, equipment, history, and anomaly APIs.
- [x] Visualize live status and trends.

## Phase 2 — Protocol and delivery depth (complete)

- [x] Add an OPC-UA address-space simulator and collector.
- [x] Containerize every component.
- [x] Add automated tests, linting, and GitHub Actions.
- [x] Document architecture, schema, API, model, testing, and deployment.

## Phase 3 — Evidence-quality model evaluation

- [ ] Create a frozen, labeled scenario dataset independent of training.
- [ ] Add time-window features and compare against the point model.
- [ ] Report false alarms per operating hour and lead-time metrics.
- [ ] Add a reproducible evaluation notebook or script and model card.

## Phase 4 — Production-readiness study

- [ ] Add Alembic migrations and PostgreSQL integration tests.
- [ ] Add MQTT TLS/authentication and API role-based access.
- [ ] Add OPC-UA subscriptions and data-quality propagation.
- [ ] Add Prometheus metrics, traces, and alert-routing boundaries.
- [ ] Measure ingest throughput and API query latency before scaling claims.
