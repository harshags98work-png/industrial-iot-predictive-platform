import asyncio
import logging

from asyncua import Client
from pydantic import ValidationError

from iiot_platform.anomaly.model import AnomalyModel
from iiot_platform.config import get_settings
from iiot_platform.db import SessionFactory, create_schema
from iiot_platform.logging_config import configure_logging
from iiot_platform.schemas import TelemetryReading
from iiot_platform.services import ingest_reading
from iiot_platform.simulators.opcua import NAMESPACE_URI

logger = logging.getLogger(__name__)
VARIABLE_NAMES = [
    "equipment_id",
    "equipment_name",
    "equipment_type",
    "location",
    "observed_at",
    "temperature_c",
    "vibration_mm_s",
    "current_a",
    "pressure_bar",
    "operating_state",
    "quality",
]


async def run() -> None:
    settings = get_settings()
    await create_schema()
    model = AnomalyModel.load(settings.model_path, settings.model_metadata_path)
    while True:
        try:
            async with Client(url=settings.opcua_url) as client:
                namespace = await client.get_namespace_index(NAMESPACE_URI)
                nodes = {
                    name: client.get_node(f"ns={namespace};s=compressor-301.{name}")
                    for name in VARIABLE_NAMES
                }
                logger.info("OPC-UA collector connected to %s", settings.opcua_url)
                while True:
                    values = {name: await node.read_value() for name, node in nodes.items()}
                    values["source_protocol"] = "opcua"
                    try:
                        reading = TelemetryReading.model_validate(values)
                        async with SessionFactory() as session:
                            _, anomaly = await ingest_reading(session, reading, model)
                        if anomaly.is_anomaly:
                            logger.warning(
                                "Anomaly detected for %s: %s",
                                reading.equipment_id,
                                anomaly.explanation,
                            )
                    except ValidationError:
                        logger.exception("Rejected invalid OPC-UA values")
                    await asyncio.sleep(settings.simulation_interval_seconds)
        except Exception:
            logger.exception("OPC-UA connection or collection failed; retrying")
            await asyncio.sleep(3)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    asyncio.run(run())


if __name__ == "__main__":
    main()
