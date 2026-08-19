# Architecture Decisions

## ADR-001: One deployable codebase, multiple process roles

**Context:** The project needs realistic boundaries without unnecessary microservice overhead.

**Decision:** Package shared domain code once and run API, trainer, simulators, and collectors as separate Docker Compose services with different commands.

**Consequences:** Process failures are isolated and responsibilities are visible, while one Python package avoids duplicated contracts. Independent release versioning is intentionally out of scope.

## ADR-002: Shared normalized telemetry contract

**Context:** MQTT messages and OPC-UA nodes have different transport shapes.

**Decision:** Convert both protocols to the same Pydantic `TelemetryReading` before persistence or scoring.

**Consequences:** Analytics and storage remain protocol-independent. Protocol-specific quality details may need richer mapping in a future version.

## ADR-003: Isolation Forest as an anomaly baseline

**Context:** The demonstration has synthetic normal-operation data but no credible real-world failure labels.

**Decision:** Use an unsupervised Isolation Forest and call its result an anomaly score, not a failure probability.

**Consequences:** The model is simple and reproducible, but cannot support claims about predictive-maintenance accuracy until a labeled evaluation is added.
