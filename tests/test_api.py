from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from iiot_platform.models import AnomalyResult, Equipment, SensorReading


async def seed_equipment(session: AsyncSession) -> None:
    equipment = Equipment(
        id="pump-test",
        name="Test Pump",
        equipment_type="centrifugal-pump",
        location="Test Cell",
        protocol="mqtt",
        created_at=datetime.now(UTC),
        active=True,
    )
    reading = SensorReading(
        equipment_id="pump-test",
        observed_at=datetime.now(UTC),
        temperature_c=68.0,
        vibration_mm_s=3.1,
        current_a=18.2,
        pressure_bar=6.4,
        operating_state="running",
        source_protocol="mqtt",
        quality="good",
    )
    session.add_all([equipment, reading])
    await session.flush()
    session.add(
        AnomalyResult(
            reading_id=reading.id,
            equipment_id="pump-test",
            scored_at=datetime.now(UTC),
            score=0.11,
            is_anomaly=False,
            model_version="test-v1",
            explanation="Baseline-like pattern.",
        )
    )
    await session.commit()


async def test_health_endpoints(client: AsyncClient) -> None:
    live = await client.get("/health/live")
    ready = await client.get("/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json()["database"] == "connected"


async def test_equipment_history_and_status(
    client: AsyncClient, session: AsyncSession
) -> None:
    await seed_equipment(session)

    equipment = await client.get("/api/v1/equipment")
    history = await client.get("/api/v1/equipment/pump-test/readings")
    status = await client.get("/api/v1/equipment/pump-test/status")

    assert equipment.status_code == 200
    assert equipment.json()[0]["id"] == "pump-test"
    assert history.json()[0]["temperature_c"] == 68.0
    assert status.json()["health"] == "normal"


async def test_missing_equipment_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/equipment/not-real/status")

    assert response.status_code == 404
