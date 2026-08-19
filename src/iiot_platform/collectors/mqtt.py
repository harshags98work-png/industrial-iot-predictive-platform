import asyncio
import logging

import aiomqtt
from pydantic import ValidationError

from iiot_platform.anomaly.model import AnomalyModel
from iiot_platform.config import get_settings
from iiot_platform.db import SessionFactory, create_schema
from iiot_platform.logging_config import configure_logging
from iiot_platform.schemas import TelemetryReading
from iiot_platform.services import ingest_reading

logger = logging.getLogger(__name__)


async def run() -> None:
    settings = get_settings()
    await create_schema()
    model = AnomalyModel.load(settings.model_path, settings.model_metadata_path)
    while True:
        try:
            async with aiomqtt.Client(settings.mqtt_host, settings.mqtt_port) as client:
                await client.subscribe(settings.mqtt_topic, qos=1)
                logger.info("MQTT collector subscribed to %s", settings.mqtt_topic)
                async for message in client.messages:
                    try:
                        reading = TelemetryReading.model_validate_json(message.payload)
                        async with SessionFactory() as session:
                            _, anomaly = await ingest_reading(session, reading, model)
                        if anomaly.is_anomaly:
                            logger.warning(
                                "Anomaly detected for %s: %s",
                                reading.equipment_id,
                                anomaly.explanation,
                            )
                    except ValidationError:
                        logger.exception("Rejected invalid MQTT payload from %s", message.topic)
                    except Exception:
                        logger.exception("Failed to process MQTT payload from %s", message.topic)
        except aiomqtt.MqttError:
            logger.exception("MQTT collector disconnected; retrying")
            await asyncio.sleep(3)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    asyncio.run(run())


if __name__ == "__main__":
    main()
