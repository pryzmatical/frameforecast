"""POST /predict -- the only stateful-feeling endpoint, and it's not stateful.

Every request is independent: validate the hardware/game/mod selections,
run them through the trained model, return a point estimate, a range, and a
feature-importance breakdown. Nothing is persisted.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data.catalog import get_game, get_mod
from app.ml.model import ModelNotLoadedError, predict as run_prediction
from app.schemas import FeatureImportanceOut, PredictRequest, PredictResponse

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if get_game(payload.game_id) is None:
        raise HTTPException(status_code=422, detail=f"Unknown game_id '{payload.game_id}'")

    category_ids: list[str] = []
    for mod_id in payload.mod_ids:
        mod = get_mod(mod_id)
        if mod is None:
            raise HTTPException(status_code=422, detail=f"Unknown mod_id '{mod_id}'")
        if mod.game_id != payload.game_id:
            raise HTTPException(
                status_code=422,
                detail=f"Mod '{mod_id}' does not belong to game '{payload.game_id}'",
            )
        category_ids.append(mod.category_id)

    try:
        result = run_prediction(
            game_id=payload.game_id,
            cpu_tier=payload.cpu_tier,
            gpu_tier=payload.gpu_tier,
            resolution=payload.resolution,
            ram_tier=payload.ram_tier,
            mod_category_ids=category_ids,
        )
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PredictResponse(
        game_id=payload.game_id,
        predicted_fps=result.predicted_fps,
        low_fps=result.low_fps,
        high_fps=result.high_fps,
        feature_importance=[
            FeatureImportanceOut(label=e.label, importance=round(e.importance, 4))
            for e in result.feature_importance
        ],
        model_version=result.model_version,
    )
