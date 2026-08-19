# Development Workflow

These are the conventions I follow while extending the project.

## Scope

The application is intentionally small enough to run on a laptop. A complete change should fit into the existing data path:

1. MQTT or OPC-UA produces a reading.
2. A collector validates it as `TelemetryReading`.
3. The ingestion service stores the reading and anomaly result.
4. FastAPI makes the data available to the dashboard or another client.

New services or frameworks should solve a measured problem rather than add another technology to the stack.

## Design conventions

- Protocol-specific behavior stays in `collectors/` and `simulators/`.
- API routes handle HTTP concerns; persistence and scoring stay in shared services.
- Sensor timestamps are stored in UTC and every value has an explicit engineering unit.
- Raw readings and derived anomaly results are separate database records.
- Model artifacts include version metadata and are generated locally instead of committed.
- Configuration comes from environment variables; credentials do not belong in the repository.
- Schema changes after the initial version should be introduced through Alembic migrations.

## Change checklist

Before considering a change complete:

1. Run the smallest relevant test while developing.
2. Run `ruff check .` and the full `pytest` suite.
3. Confirm the Docker and local-development commands still agree.
4. Update the relevant document when behavior or configuration changes.
5. Record a meaningful architecture tradeoff in `docs/decisions.md`.

## Common commands

```bash
make install
make lint
make test
make demo
make down
```
