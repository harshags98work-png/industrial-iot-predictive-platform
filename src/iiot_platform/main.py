from contextlib import asynccontextmanager

from fastapi import FastAPI

from iiot_platform import __version__
from iiot_platform.api.routes import anomalies, equipment, health
from iiot_platform.config import get_settings
from iiot_platform.db import create_schema
from iiot_platform.logging_config import configure_logging

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_schema()
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Synthetic industrial equipment monitoring and anomaly analytics API.",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(equipment.router)
app.include_router(anomalies.router)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs"}
