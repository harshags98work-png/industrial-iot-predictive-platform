# API

Interactive OpenAPI documentation is available at `/docs` when the API runs.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health/live` | Confirms the API process is alive |
| GET | `/health/ready` | Confirms the database can answer a query |
| GET | `/api/v1/equipment` | Lists discovered equipment |
| GET | `/api/v1/equipment/{id}/status` | Returns equipment, latest reading, latest score, and health |
| GET | `/api/v1/equipment/{id}/readings?limit=100` | Returns newest readings first |
| GET | `/api/v1/anomalies?equipment_id={id}&anomalous_only=true&limit=100` | Filters recent scores |

Limits are constrained to 1–1000 records to prevent accidental unbounded history responses. The MVP exposes read APIs only; authenticated configuration and maintenance mutations are roadmap items.

## Health semantics

- `normal`: latest reading is under two minutes old and the latest score is not anomalous.
- `warning`: latest reading is fresh and the latest score is anomalous.
- `offline`: no reading exists or the latest reading is more than two minutes old.
