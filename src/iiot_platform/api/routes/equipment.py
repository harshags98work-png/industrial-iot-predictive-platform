from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from iiot_platform.db import get_session
from iiot_platform.models import Equipment, SensorReading
from iiot_platform.schemas import EquipmentOut, EquipmentStatus, ReadingOut
from iiot_platform.services import equipment_status

router = APIRouter(prefix="/api/v1/equipment", tags=["equipment"])


@router.get("", response_model=list[EquipmentOut])
async def list_equipment(session: AsyncSession = Depends(get_session)) -> list[Equipment]:
    result = await session.scalars(select(Equipment).order_by(Equipment.id))
    return list(result)


@router.get("/{equipment_id}/status", response_model=EquipmentStatus)
async def get_equipment_status(
    equipment_id: str, session: AsyncSession = Depends(get_session)
) -> dict:
    equipment = await session.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return await equipment_status(session, equipment)


@router.get("/{equipment_id}/readings", response_model=list[ReadingOut])
async def get_readings(
    equipment_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> list[SensorReading]:
    if await session.get(Equipment, equipment_id) is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    result = await session.scalars(
        select(SensorReading)
        .where(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.observed_at))
        .limit(limit)
    )
    return list(result)
