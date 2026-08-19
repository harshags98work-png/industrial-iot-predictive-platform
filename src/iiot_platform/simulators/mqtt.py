import asyncio
import logging

import aiomqtt

from iiot_platform.config import get_settings
from iiot_platform.logging_config import configure_logging
from iiot_platform.simulators.common import EquipmentSignalGenerator

logger = logging.getLogger(__name__)

EQUIPMENT = [
    ("pump-101", "Cooling Water Pump 101", "centrifugal-pump", "Line A"),
    ("motor-201", "Conveyor Motor 201", "induction-motor", "Line B"),
]


async def run() -> None:
    settings = get_settings()
    generator = EquipmentSignalGenerator(seed=101)
    while True:
        try:
            async with aiomqtt.Client(settings.mqtt_host, settings.mqtt_port) as client:
                logger.info(
                    "MQTT simulator connected to %s:%s",
                    settings.mqtt_host,
                    settings.mqtt_port,
                )
                while True:
                    for equipment_id, name, equipment_type, location in EQUIPMENT:
                        reading = generator.reading(
                            equipment_id, name, equipment_type, location, "mqtt"
                        )
                        topic = f"factory/{equipment_id}/telemetry"
                        await client.publish(topic, reading.model_dump_json(), qos=1)
                    await asyncio.sleep(settings.simulation_interval_seconds)
        except aiomqtt.MqttError:
            logger.exception("MQTT simulator disconnected; retrying")
            await asyncio.sleep(3)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    asyncio.run(run())


if __name__ == "__main__":
    main()
