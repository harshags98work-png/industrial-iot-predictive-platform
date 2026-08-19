from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from iiot_platform.anomaly.model import AnomalyModel, ScoreResult
from iiot_platform.models import AnomalyResult, Equipment, SensorReading
from iiot_platform.schemas import TelemetryReading


async def ingest_reading(
    session: AsyncSession, reading: TelemetryReading, model: AnomalyModel
) -> tuple[SensorReading, AnomalyResult]:
    equipment = await session.get(Equipment, reading.equipment_id)
    if equipment is None:
        equipment = Equipment(
            id=reading.equipment_id,
            name=reading.equipment_name,
            equipment_type=reading.equipment_type,
            location=reading.location,
            protocol=reading.source_protocol,
            created_at=datetime.now(UTC),
            active=True,
        )
        session.add(equipment)
    else:
        equipment.protocol = reading.source_protocol
        equipment.active = True

    score = model.score(reading.feature_vector())
    stored_reading = SensorReading(
        equipment_id=reading.equipment_id,
        observed_at=reading.observed_at,
        temperature_c=reading.temperature_c,
        vibration_mm_s=reading.vibration_mm_s,
        current_a=reading.current_a,
        pressure_bar=reading.pressure_bar,
        operating_state=reading.operating_state,
        source_protocol=reading.source_protocol,
        quality=reading.quality,
    )
    session.add(stored_reading)
    await session.flush()

    stored_anomaly = anomaly_from_score(stored_reading, score)
    session.add(stored_anomaly)
    await session.commit()
    await session.refresh(stored_reading)
    await session.refresh(stored_anomaly)
    return stored_reading, stored_anomaly


def anomaly_from_score(reading: SensorReading, score: ScoreResult) -> AnomalyResult:
    return AnomalyResult(
        reading_id=reading.id,
        equipment_id=reading.equipment_id,
        scored_at=datetime.now(UTC),
        score=score.score,
        is_anomaly=score.is_anomaly,
        model_version=score.model_version,
        explanation=score.explanation,
    )


async def equipment_status(session: AsyncSession, equipment: Equipment) -> dict:
    reading = await session.scalar(
        select(SensorReading)
        .where(SensorReading.equipment_id == equipment.id)
        .order_by(desc(SensorReading.observed_at))
        .limit(1)
    )
    anomaly = await session.scalar(
        select(AnomalyResult)
        .where(AnomalyResult.equipment_id == equipment.id)
        .order_by(desc(AnomalyResult.scored_at))
        .limit(1)
    )
    last_seen = reading.observed_at if reading else None
    if last_seen is not None and last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=UTC)
    if last_seen is None or last_seen < datetime.now(UTC) - timedelta(minutes=2):
        health = "offline"
    elif anomaly and anomaly.is_anomaly:
        health = "warning"
    else:
        health = "normal"
    return {
        "equipment": equipment,
        "latest_reading": reading,
        "latest_anomaly": anomaly,
        "health": health,
    }
