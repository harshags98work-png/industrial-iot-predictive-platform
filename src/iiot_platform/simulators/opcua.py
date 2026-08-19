import asyncio
import logging

from asyncua import Server, ua

from iiot_platform.config import get_settings
from iiot_platform.logging_config import configure_logging
from iiot_platform.simulators.common import EquipmentSignalGenerator

logger = logging.getLogger(__name__)
NAMESPACE_URI = "urn:portfolio:industrial-iot"


async def run() -> None:
    settings = get_settings()
    server = Server()
    await server.init()
    server.set_endpoint(settings.opcua_bind_url)
    server.set_server_name("Portfolio Industrial IoT OPC-UA Simulator")
    namespace = await server.register_namespace(NAMESPACE_URI)
    machine = await server.nodes.objects.add_object(
        ua.NodeId("compressor-301", namespace), "Compressor 301"
    )
    variables = {}
    initial_values = {
        "equipment_id": "compressor-301",
        "equipment_name": "Air Compressor 301",
        "equipment_type": "rotary-screw-compressor",
        "location": "Utilities",
        "observed_at": "",
        "temperature_c": 0.0,
        "vibration_mm_s": 0.0,
        "current_a": 0.0,
        "pressure_bar": 0.0,
        "operating_state": "running",
        "quality": "good",
    }
    for name, initial_value in initial_values.items():
        variables[name] = await machine.add_variable(
            ua.NodeId(f"compressor-301.{name}", namespace), name, initial_value
        )

    generator = EquipmentSignalGenerator(seed=301)
    async with server:
        logger.info("OPC-UA simulator listening on %s", settings.opcua_bind_url)
        while True:
            reading = generator.reading(
                "compressor-301",
                "Air Compressor 301",
                "rotary-screw-compressor",
                "Utilities",
                "opcua",
            )
            values = reading.model_dump(mode="json")
            for name, node in variables.items():
                await node.write_value(values[name])
            await asyncio.sleep(settings.simulation_interval_seconds)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    asyncio.run(run())


if __name__ == "__main__":
    main()
