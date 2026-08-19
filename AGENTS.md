# Industrial IoT Project Copilot

## Mission

Help the owner design, implement, test, explain, and finish this portfolio project as a credible industrial-IoT system. Prefer a small, working vertical slice over broad but unverified claims.

## Product boundary

The platform must demonstrate this path end to end:

1. Simulators produce equipment telemetry through MQTT and OPC-UA.
2. Collectors validate and normalize telemetry.
3. PostgreSQL stores equipment, readings, anomalies, events, and maintenance records.
4. A scikit-learn model scores readings and records explainable anomaly results.
5. FastAPI exposes health, equipment, history, and anomaly endpoints.
6. A dashboard displays current health, trends, and anomaly context.
7. Docker Compose starts the complete demo locally.
8. Tests and CI make the result safe to publish.

Do not introduce a cloud service, message broker, framework, or microservice unless it closes a documented requirement. Do not claim production scale, predictive maintenance accuracy, or real factory integration without evidence.

## Architecture rules

- Keep protocol adapters at the edge. Both MQTT and OPC-UA must emit the same `TelemetryReading` domain shape.
- Keep API routes thin. Business and persistence behavior belongs in services or repositories.
- Treat UTC timestamps, equipment identity, engineering units, and data quality as first-class fields.
- Store raw sensor values and derived anomaly results separately.
- Keep model artifacts versioned by metadata, but do not commit generated binary artifacts.
- Use schema migrations for persistent database changes after the MVP baseline.
- Prefer configuration through environment variables. Never commit secrets.
- Add structured logs at protocol, persistence, model, and API boundaries.

## Delivery workflow

For every requested feature:

1. State the user-visible outcome and acceptance criteria.
2. Identify affected components and the smallest vertical change.
3. Implement the change with typed interfaces and useful failure messages.
4. Add or update tests for observable behavior.
5. Run the narrow tests, then the full quality suite.
6. Update the relevant documentation and the roadmap checkbox.
7. Summarize what is demonstrated, what is simulated, and what remains.

When architecture is unclear, record the decision in `docs/decisions.md` with context, choice, and consequences. When blocked by missing user input, offer a recommended default and explain the tradeoff.

## Definition of done

A change is complete only when:

- it runs from the documented commands;
- tests cover its important behavior;
- logs and errors make failures diagnosable;
- Docker and local-development paths remain aligned;
- public documentation matches the implementation;
- no resume or README statement overclaims what the repository proves.

## Useful commands

- `make install` — install development dependencies.
- `make test` — run the test suite.
- `make lint` — run static quality checks.
- `make demo` — start the full Docker Compose demo.
- `make down` — stop the demo.
