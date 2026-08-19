from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    equipment_type: Mapped[str] = mapped_column(String(64))
    location: Mapped[str] = mapped_column(String(120))
    protocol: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    readings: Mapped[list["SensorReading"]] = relationship(back_populates="equipment")


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (
        Index("ix_readings_equipment_timestamp", "equipment_id", "observed_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("equipment.id", ondelete="CASCADE"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    temperature_c: Mapped[float] = mapped_column(Float)
    vibration_mm_s: Mapped[float] = mapped_column(Float)
    current_a: Mapped[float] = mapped_column(Float)
    pressure_bar: Mapped[float] = mapped_column(Float)
    operating_state: Mapped[str] = mapped_column(String(32))
    source_protocol: Mapped[str] = mapped_column(String(16))
    quality: Mapped[str] = mapped_column(String(16), default="good")

    equipment: Mapped[Equipment] = relationship(back_populates="readings")
    anomaly: Mapped["AnomalyResult | None"] = relationship(back_populates="reading")


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reading_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_readings.id", ondelete="CASCADE"), unique=True
    )
    equipment_id: Mapped[str] = mapped_column(String(64), index=True)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    score: Mapped[float] = mapped_column(Float)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, index=True)
    model_version: Mapped[str] = mapped_column(String(64))
    explanation: Mapped[str] = mapped_column(Text)

    reading: Mapped[SensorReading] = relationship(back_populates="anomaly")


class MaintenanceEvent(Base):
    __tablename__ = "maintenance_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("equipment.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SystemEvent(Base):
    __tablename__ = "system_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    component: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
