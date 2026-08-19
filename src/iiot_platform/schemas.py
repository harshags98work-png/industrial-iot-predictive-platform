from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TelemetryReading(BaseModel):
    equipment_id: str = Field(min_length=2, max_length=64)
    equipment_name: str = Field(min_length=2, max_length=120)
    equipment_type: str = Field(min_length=2, max_length=64)
    location: str = Field(min_length=2, max_length=120)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    temperature_c: float = Field(ge=-50, le=250)
    vibration_mm_s: float = Field(ge=0, le=100)
    current_a: float = Field(ge=0, le=1000)
    pressure_bar: float = Field(ge=0, le=1000)
    operating_state: Literal["running", "idle", "fault"] = "running"
    source_protocol: Literal["mqtt", "opcua"]
    quality: Literal["good", "uncertain", "bad"] = "good"

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def feature_vector(self) -> list[float]:
        return [self.temperature_c, self.vibration_mm_s, self.current_a, self.pressure_bar]


class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    equipment_type: str
    location: str
    protocol: str
    created_at: datetime
    active: bool


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: str
    observed_at: datetime
    temperature_c: float
    vibration_mm_s: float
    current_a: float
    pressure_bar: float
    operating_state: str
    source_protocol: str
    quality: str


class AnomalyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reading_id: int
    equipment_id: str
    scored_at: datetime
    score: float
    is_anomaly: bool
    model_version: str
    explanation: str


class EquipmentStatus(BaseModel):
    equipment: EquipmentOut
    latest_reading: ReadingOut | None
    latest_anomaly: AnomalyOut | None
    health: Literal["normal", "warning", "offline"]
