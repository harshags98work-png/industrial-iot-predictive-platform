from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from iiot_platform.db import get_session
from iiot_platform.models import AnomalyResult
from iiot_platform.schemas import AnomalyOut

router = APIRouter(prefix="/api/v1/anomalies", tags=["anomalies"])


@router.get("", response_model=list[AnomalyOut])
async def list_anomalies(
    equipment_id: str | None = None,
    anomalous_only: bool = True,
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> list[AnomalyResult]:
    query = select(AnomalyResult)
    if equipment_id:
        query = query.where(AnomalyResult.equipment_id == equipment_id)
    if anomalous_only:
        query = query.where(AnomalyResult.is_anomaly.is_(True))
    result = await session.scalars(query.order_by(desc(AnomalyResult.scored_at)).limit(limit))
    return list(result)
