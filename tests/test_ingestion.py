from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from iiot_platform.anomaly.model import ScoreResult
from iiot_platform.models import Equipment
from iiot_platform.schemas import TelemetryReading
from iiot_platform.services import ingest_reading


class FixedModel:
    def score(self, _: list[float]) -> ScoreResult:
        return ScoreResult(-0.4, True, "fixed-test", "Injected test anomaly.")


async def test_ingestion_creates_equipment_reading_and_anomaly(session: AsyncSession) -> None:
    telemetry = TelemetryReading(
        equipment_id="motor-test",
        equipment_name="Test Motor",
        equipment_type="induction-motor",
        location="QA Cell",
        observed_at=datetime.now(UTC),
        temperature_c=93,
        vibration_mm_s=9,
        current_a=31,
        pressure_bar=4,
        operating_state="fault",
        source_protocol="mqtt",
    )

    reading, anomaly = await ingest_reading(session, telemetry, FixedModel())  # type: ignore[arg-type]

    equipment = await session.get(Equipment, "motor-test")
    assert equipment is not None
    assert reading.id is not None
    assert anomaly.reading_id == reading.id
    assert anomaly.is_anomaly is True
