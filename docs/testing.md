# Testing Approach

The automated suite covers three boundaries:

1. **Model behavior:** an extreme injected fault must score below a normal vector; saved artifacts must load reproducibly.
2. **Ingestion contract:** one validated telemetry object must create linked equipment, reading, and anomaly rows.
3. **API behavior:** health, equipment history, status, and not-found responses run against an isolated SQLite database.

Run locally with:

```bash
pytest --cov=iiot_platform --cov-report=term-missing
ruff check .
docker compose config --quiet
```

SQLite keeps unit and API tests fast, while PostgreSQL remains the runtime database. A future integration-test job should start PostgreSQL, Mosquitto, and the OPC-UA server, then assert an emitted message is visible through the API.
