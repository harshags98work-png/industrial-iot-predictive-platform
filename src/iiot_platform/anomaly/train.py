import logging

import numpy as np

from iiot_platform.anomaly.model import AnomalyModel
from iiot_platform.config import get_settings
from iiot_platform.logging_config import configure_logging

logger = logging.getLogger(__name__)


def generate_baseline_samples(count: int = 5000, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    temperature = rng.normal(67, 4.5, count)
    vibration = np.clip(rng.normal(3.0, 0.7, count), 0.2, None)
    current = rng.normal(18, 2.2, count)
    pressure = rng.normal(6.5, 0.6, count)
    return np.column_stack([temperature, vibration, current, pressure])


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    samples = generate_baseline_samples()
    model = AnomalyModel.train(samples, threshold=settings.anomaly_threshold)
    model.save(settings.model_path, settings.model_metadata_path)
    logger.info("Trained model %s using %s baseline samples", model.version, len(samples))


if __name__ == "__main__":
    main()
