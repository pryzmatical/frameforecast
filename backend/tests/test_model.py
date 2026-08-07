import pytest

from app.ml import model as model_module
from app.ml.dataset import generate_training_data
from app.ml.model import ModelNotLoadedError, load_model, predict


def test_generate_training_data_shape_and_range():
    df = generate_training_data(samples_per_combo=2)
    assert len(df) > 100
    assert (df["fps"] > 0).all()
    assert df["fps"].max() < 400  # sanity bound, nothing runaway


def test_load_model_raises_clear_error_when_artifact_missing(monkeypatch, tmp_path):
    fake_path = tmp_path / "does_not_exist.joblib"
    monkeypatch.setattr(model_module, "MODEL_PATH", fake_path)
    monkeypatch.setattr(model_module, "_artifact", None)

    with pytest.raises(ModelNotLoadedError):
        load_model(force_reload=True)

    # Restore global state for other tests in the session.
    monkeypatch.setattr(model_module, "_artifact", None)


def test_predict_returns_sane_bounds_and_importance():
    result = predict(
        game_id="minecraft_java",
        cpu_tier="cpu_high",
        gpu_tier="gpu_enthusiast",
        resolution="1080p",
        ram_tier="ram_32",
        mod_category_ids=["graphics_overhaul"],
    )
    assert result.low_fps <= result.predicted_fps <= result.high_fps
    assert result.predicted_fps > 0
    labels = {e.label for e in result.feature_importance}
    assert "Game" in labels
    assert "GPU tier" in labels
