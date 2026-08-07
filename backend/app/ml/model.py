"""Loads the trained model artifact and turns it into predictions.

The uncertainty band isn't a made-up +/- percentage: RandomForestRegressor
fits many independent decision trees on bootstrapped samples, so asking each
tree for its own prediction and looking at the spread across trees gives a
genuine (if still simplified) model-native estimate of how confident the
model is for that specific input. Tight agreement across trees -> narrow
band; the trees disagree -> wider band. It is still just this model's
internal uncertainty, not a statement about real-world variance -- see
docs/METHODOLOGY.md.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.data.catalog import get_mod_category
from app.ml.dataset import CATEGORY_IDS, FEATURE_COLUMNS, build_feature_row
from app.ml.train_model import MODEL_PATH

_FEATURE_LABELS = {
    "cpu_rank": "CPU tier",
    "gpu_rank": "GPU tier",
    "resolution_rank": "Resolution",
    "ram_rank": "System RAM",
    "total_mod_count": "Total mods installed",
}
for _cat_id in CATEGORY_IDS:
    _category = get_mod_category(_cat_id)
    _FEATURE_LABELS[f"count_{_cat_id}"] = (
        f"{_category.label} mods" if _category else _cat_id
    )


class ModelNotLoadedError(RuntimeError):
    """Raised when the trained model artifact can't be found on disk."""


@dataclass
class FeatureImportanceEntry:
    feature: str
    label: str
    importance: float


@dataclass
class PredictionResult:
    predicted_fps: float
    low_fps: float
    high_fps: float
    feature_importance: list[FeatureImportanceEntry] = field(default_factory=list)
    model_version: str = ""


_lock = threading.Lock()
_artifact: dict | None = None


def _friendly_label(raw_feature_name: str) -> str:
    # ColumnTransformer output names look like "game__game_skyrim_se" or
    # "numeric__cpu_rank". Group every one-hot "game" column into one label.
    if raw_feature_name.startswith("game__"):
        return "Game"
    bare = raw_feature_name.split("__", 1)[-1]
    return _FEATURE_LABELS.get(bare, bare)


def load_model(force_reload: bool = False) -> dict:
    global _artifact
    with _lock:
        if _artifact is not None and not force_reload:
            return _artifact
        if not Path(MODEL_PATH).exists():
            raise ModelNotLoadedError(
                f"No trained model found at {MODEL_PATH}. Run "
                "`python -m app.ml.train_model` from the backend/ directory first."
            )
        _artifact = joblib.load(MODEL_PATH)
        return _artifact


def grouped_feature_importance(artifact: dict) -> list[FeatureImportanceEntry]:
    grouped: dict[str, float] = {}
    for raw_name, importance in artifact["feature_importances"].items():
        label = _friendly_label(raw_name)
        grouped[label] = grouped.get(label, 0.0) + importance

    total = sum(grouped.values()) or 1.0
    entries = [
        FeatureImportanceEntry(feature=label, label=label, importance=value / total)
        for label, value in grouped.items()
    ]
    entries.sort(key=lambda e: e.importance, reverse=True)
    return entries


def predict(
    game_id: str,
    cpu_tier: str,
    gpu_tier: str,
    resolution: str,
    ram_tier: str,
    mod_category_ids: list[str],
) -> PredictionResult:
    artifact = load_model()
    pipeline = artifact["pipeline"]

    row = build_feature_row(game_id, cpu_tier, gpu_tier, resolution, ram_tier, mod_category_ids)
    X = pd.DataFrame([row])[FEATURE_COLUMNS]

    point_estimate = float(pipeline.predict(X)[0])

    # Per-tree spread -> uncertainty band.
    preprocessor = pipeline.named_steps["preprocess"]
    forest = pipeline.named_steps["model"]
    X_transformed = preprocessor.transform(X)
    tree_preds = np.array([tree.predict(X_transformed)[0] for tree in forest.estimators_])
    std = float(tree_preds.std())

    # Floor the band width so a lucky unanimous forest doesn't render as a
    # falsely precise single number, and never let the low end go negative.
    band = max(std, point_estimate * 0.04)
    low = max(point_estimate - band, 1.0)
    high = point_estimate + band

    return PredictionResult(
        predicted_fps=round(point_estimate, 1),
        low_fps=round(low, 1),
        high_fps=round(high, 1),
        feature_importance=grouped_feature_importance(artifact),
        model_version=artifact.get("version", "unknown"),
    )
