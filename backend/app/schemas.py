"""Pydantic request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.data.catalog import CPU_TIERS, GPU_TIERS, RAM_TIERS, RESOLUTIONS


class TierOut(BaseModel):
    id: str
    label: str
    example_parts: str


class GameOut(BaseModel):
    id: str
    name: str
    short_description: str


class ModOut(BaseModel):
    id: str
    name: str
    category_id: str
    note: str = ""


class ModCategoryOut(BaseModel):
    id: str
    label: str
    description: str


class CatalogOut(BaseModel):
    games: list[GameOut]
    cpu_tiers: list[TierOut]
    gpu_tiers: list[TierOut]
    ram_tiers: list[TierOut]
    resolutions: list[TierOut]
    mod_categories: list[ModCategoryOut]


class GameModsOut(BaseModel):
    game_id: str
    mods: list[ModOut]


_VALID_CPU = {t.id for t in CPU_TIERS}
_VALID_GPU = {t.id for t in GPU_TIERS}
_VALID_RAM = {t.id for t in RAM_TIERS}
_VALID_RES = {t.id for t in RESOLUTIONS}


class PredictRequest(BaseModel):
    game_id: str
    cpu_tier: str
    gpu_tier: str
    ram_tier: str
    resolution: str
    mod_ids: list[str] = Field(default_factory=list)

    @field_validator("cpu_tier")
    @classmethod
    def validate_cpu(cls, v: str) -> str:
        if v not in _VALID_CPU:
            raise ValueError(f"Unknown cpu_tier '{v}'. Valid options: {sorted(_VALID_CPU)}")
        return v

    @field_validator("gpu_tier")
    @classmethod
    def validate_gpu(cls, v: str) -> str:
        if v not in _VALID_GPU:
            raise ValueError(f"Unknown gpu_tier '{v}'. Valid options: {sorted(_VALID_GPU)}")
        return v

    @field_validator("ram_tier")
    @classmethod
    def validate_ram(cls, v: str) -> str:
        if v not in _VALID_RAM:
            raise ValueError(f"Unknown ram_tier '{v}'. Valid options: {sorted(_VALID_RAM)}")
        return v

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        if v not in _VALID_RES:
            raise ValueError(f"Unknown resolution '{v}'. Valid options: {sorted(_VALID_RES)}")
        return v


class FeatureImportanceOut(BaseModel):
    label: str
    importance: float


class PredictResponse(BaseModel):
    game_id: str
    predicted_fps: float
    low_fps: float
    high_fps: float
    feature_importance: list[FeatureImportanceOut]
    model_version: str
    disclaimer: str = (
        "This is a statistical estimate from a small, hand-curated training set, "
        "not a simulation or measurement of actual gameplay. Real-world results "
        "will vary. See /methodology in the app for details."
    )
