"""Read-only reference data: games, hardware tiers, and the mod library."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data.catalog import (
    CPU_TIERS,
    GAMES,
    GPU_TIERS,
    MOD_CATEGORIES,
    RAM_TIERS,
    RESOLUTIONS,
    get_game,
    mods_for_game,
)
from app.schemas import (
    CatalogOut,
    GameModsOut,
    GameOut,
    ModCategoryOut,
    ModOut,
    TierOut,
)

router = APIRouter(tags=["catalog"])


@router.get("/catalog", response_model=CatalogOut)
def get_catalog() -> CatalogOut:
    """Everything the frontend form needs in one call: games, hardware tiers,
    resolutions, and mod categories. Mods themselves are fetched per-game
    since each game has its own library.
    """
    return CatalogOut(
        games=[GameOut(**vars(g)) for g in GAMES],
        cpu_tiers=[TierOut(id=t.id, label=t.label, example_parts=t.example_parts) for t in CPU_TIERS],
        gpu_tiers=[TierOut(id=t.id, label=t.label, example_parts=t.example_parts) for t in GPU_TIERS],
        ram_tiers=[TierOut(id=t.id, label=t.label, example_parts=t.example_parts) for t in RAM_TIERS],
        resolutions=[TierOut(id=t.id, label=t.label, example_parts=t.example_parts) for t in RESOLUTIONS],
        mod_categories=[
            ModCategoryOut(id=c.id, label=c.label, description=c.description)
            for c in MOD_CATEGORIES
        ],
    )


@router.get("/games/{game_id}/mods", response_model=GameModsOut)
def get_game_mods(game_id: str) -> GameModsOut:
    if get_game(game_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown game '{game_id}'")
    mods = mods_for_game(game_id)
    return GameModsOut(
        game_id=game_id,
        mods=[ModOut(id=m.id, name=m.name, category_id=m.category_id, note=m.note) for m in mods],
    )
