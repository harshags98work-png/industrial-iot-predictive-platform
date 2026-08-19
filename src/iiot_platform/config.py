from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Industrial IoT Platform"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./iiot.db"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "factory/+/telemetry"
    opcua_url: str = "opc.tcp://localhost:4840/factory/server/"
    opcua_bind_url: str = "opc.tcp://0.0.0.0:4840/factory/server/"
    model_path: str = "artifacts/isolation_forest.joblib"
    model_metadata_path: str = "artifacts/model_metadata.json"
    anomaly_threshold: float = -0.02
    api_base_url: str = "http://localhost:8000"
    simulation_interval_seconds: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
