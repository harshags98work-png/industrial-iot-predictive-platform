import numpy as np

from iiot_platform.anomaly.model import AnomalyModel
from iiot_platform.anomaly.train import generate_baseline_samples


def test_extreme_fault_scores_lower_than_normal_reading() -> None:
    samples = generate_baseline_samples(count=800)
    model = AnomalyModel.train(samples, threshold=-0.02)

    normal = model.score([67.0, 3.0, 18.0, 6.5])
    fault = model.score([102.0, 12.0, 36.0, 2.0])

    assert fault.score < normal.score
    assert fault.is_anomaly is True
    assert normal.is_anomaly is False
    assert "high temperature" in fault.explanation


def test_model_artifact_round_trip(tmp_path) -> None:
    samples = np.asarray(
        [[65.0, 3.0, 18.0, 6.5], [66.0, 3.2, 17.5, 6.4], [67.0, 2.8, 18.5, 6.7]]
        * 50
    )
    model = AnomalyModel.train(samples, version="test-v1")
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "metadata.json"

    model.save(str(model_path), str(metadata_path))
    restored = AnomalyModel.load(str(model_path), str(metadata_path))

    assert restored.version == "test-v1"
    assert restored.score([66.0, 3.0, 18.0, 6.5]).score == model.score(
        [66.0, 3.0, 18.0, 6.5]
    ).score
