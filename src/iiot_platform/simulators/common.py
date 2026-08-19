from datetime import UTC, datetime

import numpy as np

from iiot_platform.schemas import TelemetryReading


class EquipmentSignalGenerator:
    """Generate correlated normal signals and repeatable, time-boxed faults."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = np.random.default_rng(seed)
        self.step = 0

    def reading(
        self,
        equipment_id: str,
        name: str,
        equipment_type: str,
        location: str,
        protocol: str,
    ) -> TelemetryReading:
        cycle = self.step % 120
        bearing_fault = 70 <= cycle < 90
        overheating = 95 <= cycle < 108
        self.step += 1

        load = float(self.rng.normal(0, 1))
        temperature = 67 + 2.0 * load + self.rng.normal(0, 1.2)
        vibration = 3.0 + 0.25 * load + self.rng.normal(0, 0.25)
        current = 18 + 1.2 * load + self.rng.normal(0, 0.6)
        pressure = 6.5 + 0.15 * load + self.rng.normal(0, 0.15)
        state = "running"

        if bearing_fault:
            vibration += 6.0 + float(self.rng.normal(0, 0.6))
            current += 5.0
            state = "fault"
        if overheating:
            temperature += 27.0
            current += 8.0
            pressure -= 2.2
            state = "fault"

        return TelemetryReading(
            equipment_id=equipment_id,
            equipment_name=name,
            equipment_type=equipment_type,
            location=location,
            observed_at=datetime.now(UTC),
            temperature_c=round(float(temperature), 3),
            vibration_mm_s=round(max(0.0, float(vibration)), 3),
            current_a=round(max(0.0, float(current)), 3),
            pressure_bar=round(max(0.0, float(pressure)), 3),
            operating_state=state,
            source_protocol=protocol,
            quality="good",
        )
