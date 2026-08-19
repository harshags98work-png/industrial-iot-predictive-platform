import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = ["temperature_c", "vibration_mm_s", "current_a", "pressure_bar"]


@dataclass(frozen=True)
class ScoreResult:
    score: float
    is_anomaly: bool
    model_version: str
    explanation: str


class AnomalyModel:
    def __init__(self, pipeline: Pipeline, version: str, threshold: float = -0.02) -> None:
        self.pipeline = pipeline
        self.version = version
        self.threshold = threshold

    @classmethod
    def train(
        cls, samples: np.ndarray, version: str = "isolation-forest-v1", threshold: float = -0.02
    ) -> "AnomalyModel":
        pipeline = Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    IsolationForest(
                        n_estimators=150,
                        contamination=0.04,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        pipeline.fit(samples)
        return cls(pipeline, version, threshold)

    def score(self, features: list[float]) -> ScoreResult:
        vector = np.asarray([features], dtype=float)
        score = float(self.pipeline.decision_function(vector)[0])
        is_anomaly = score < self.threshold
        explanation = self._explain(features, score, is_anomaly)
        return ScoreResult(score, is_anomaly, self.version, explanation)

    def save(self, model_path: str, metadata_path: str) -> None:
        model_file = Path(model_path)
        metadata_file = Path(metadata_path)
        model_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, model_file)
        metadata_file.write_text(
            json.dumps(
                {
                    "version": self.version,
                    "threshold": self.threshold,
                    "features": FEATURE_NAMES,
                    "method": "IsolationForest with StandardScaler",
                },
                indent=2,
            )
        )

    @classmethod
    def load(cls, model_path: str, metadata_path: str) -> "AnomalyModel":
        pipeline = joblib.load(model_path)
        metadata = json.loads(Path(metadata_path).read_text())
        return cls(pipeline, metadata["version"], float(metadata["threshold"]))

    @staticmethod
    def _explain(features: list[float], score: float, is_anomaly: bool) -> str:
        temperature, vibration, current, pressure = features
        signals: list[str] = []
        if temperature > 85:
            signals.append("high temperature")
        if vibration > 7:
            signals.append("high vibration")
        if current > 28:
            signals.append("high motor current")
        if pressure < 3:
            signals.append("low pressure")
        if not signals:
            summary = (
                "multivariate pattern outside the learned baseline"
                if is_anomaly
                else "baseline-like pattern"
            )
            signals.append(summary)
        return f"Score {score:.4f}; " + ", ".join(signals) + "."
