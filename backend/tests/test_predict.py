import pytest

VALID_PAYLOAD = {
    "game_id": "cyberpunk_2077",
    "cpu_tier": "cpu_mid",
    "gpu_tier": "gpu_upper_mid",
    "ram_tier": "ram_16",
    "resolution": "1080p",
    "mod_ids": [],
}


def test_predict_valid_input_returns_estimate_and_range(client):
    resp = client.post("/predict", json=VALID_PAYLOAD)
    assert resp.status_code == 200
    body = resp.json()

    assert body["predicted_fps"] > 0
    assert body["low_fps"] <= body["predicted_fps"] <= body["high_fps"]
    assert body["low_fps"] > 0
    assert body["feature_importance"], "expected a non-empty feature importance breakdown"
    assert body["disclaimer"]
    # The disclaimer should explicitly disclaim "simulation," not claim to be one.
    assert "not a simulation" in body["disclaimer"].lower()


def test_predict_with_mods_changes_the_estimate(client):
    baseline = client.post("/predict", json=VALID_PAYLOAD).json()

    with_mods = client.post(
        "/predict",
        json={**VALID_PAYLOAD, "mod_ids": ["cp77_reshade", "cp77_texture_pack"]},
    ).json()

    # Graphics-heavy mods should pull the estimate down, not leave it unchanged.
    assert with_mods["predicted_fps"] < baseline["predicted_fps"]


def test_feature_importance_sums_to_roughly_one(client):
    resp = client.post("/predict", json=VALID_PAYLOAD)
    body = resp.json()
    total = sum(entry["importance"] for entry in body["feature_importance"])
    assert total == pytest.approx(1.0, abs=0.01)


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("game_id", "not_a_real_game"),
        ("cpu_tier", "cpu_ultra_mega"),
        ("gpu_tier", "gpu_potato"),
        ("ram_tier", "ram_1000"),
        ("resolution", "8k"),
    ],
)
def test_predict_rejects_unknown_hardware_values(client, field, bad_value):
    payload = {**VALID_PAYLOAD, field: bad_value}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422


def test_predict_rejects_mod_from_a_different_game(client):
    payload = {**VALID_PAYLOAD, "mod_ids": ["skyrim_enb"]}  # Skyrim mod, Cyberpunk request
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422


def test_predict_rejects_unknown_mod_id(client):
    payload = {**VALID_PAYLOAD, "mod_ids": ["not_a_real_mod"]}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 422


def test_predict_works_for_every_supported_game(client):
    for game_id in ("skyrim_se", "cyberpunk_2077", "minecraft_java"):
        resp = client.post("/predict", json={**VALID_PAYLOAD, "game_id": game_id})
        assert resp.status_code == 200, resp.text
        assert resp.json()["predicted_fps"] > 0


def test_model_not_loaded_returns_503(client, monkeypatch):
    from app.routers import predict as predict_router

    def _boom(**kwargs):
        from app.ml.model import ModelNotLoadedError

        raise ModelNotLoadedError("model artifact missing for test")

    monkeypatch.setattr(predict_router, "run_prediction", _boom)
    resp = client.post("/predict", json=VALID_PAYLOAD)
    assert resp.status_code == 503
