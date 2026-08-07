"""Builds the synthetic training dataset the model is trained on.

FrameForecast doesn't have access to real, systematically-measured per-mod
FPS benchmarks (nobody publishes a controlled benchmark matrix of "this exact
mod combination on this exact hardware tier"). Instead, training rows are
*generated* by combining two hand-curated, documented pieces:

1. `baseline_benchmarks.py` -- approximate no-mod FPS by game/CPU/GPU/resolution.
2. The mod-impact model below -- category-level FPS impact weights, scaled by
   whichever hardware tier each category is most sensitive to, applied
   multiplicatively with a bit of random noise.

The regression model then learns to reproduce (and generalize across) that
combined function. This is an honest, documented approximation for a
portfolio project, not a claim that these are measured real-world results.
See docs/METHODOLOGY.md.
"""

from __future__ import annotations

import random

import pandas as pd

from app.data.baseline_benchmarks import CPU_ORDER, GPU_ORDER, RES_ORDER, baseline_fps
from app.data.catalog import GAMES, MOD_CATEGORIES, RAM_TIERS, get_mod_category

RAM_ORDER = [t.id for t in RAM_TIERS]

# How much a tier away from "reference" scales a sensitive mod's impact.
# Weaker hardware (lower index) feels the impact more; stronger hardware
# feels it less. Index 1 (mid CPU / upper-mid-ish GPU) is treated as ~neutral.
_GPU_SENSITIVITY_SCALE = {
    "gpu_entry": 1.45,
    "gpu_mid": 1.15,
    "gpu_upper_mid": 1.00,
    "gpu_high": 0.80,
    "gpu_enthusiast": 0.65,
}
_CPU_SENSITIVITY_SCALE = {
    "cpu_entry": 1.35,
    "cpu_mid": 1.00,
    "cpu_high": 0.75,
}

# Texture/graphics mods stream more data; low system RAM makes that worse.
_RAM_STUTTER_PENALTY = {
    "ram_8": 0.10,
    "ram_16": 0.02,
    "ram_32": 0.0,
}
_VRAM_SENSITIVE_CATEGORIES = {"texture_overhaul", "graphics_overhaul"}

# Multiplicative stacking of many mods would be unrealistically punishing, so
# the combined reduction is floored -- hardware doesn't go to zero FPS just
# because five mods are installed.
_MAX_TOTAL_REDUCTION = 0.80  # never estimate more than an 80% FPS loss from mods


def mod_effective_impact(category_id: str, cpu_tier: str, gpu_tier: str) -> float:
    """Fractional FPS reduction for one mod in this category, on this hardware."""
    category = get_mod_category(category_id)
    if category is None:
        return 0.0
    if category.sensitivity == "gpu":
        scale = _GPU_SENSITIVITY_SCALE[gpu_tier]
    elif category.sensitivity == "cpu":
        scale = _CPU_SENSITIVITY_SCALE[cpu_tier]
    else:
        scale = 1.0
    return category.base_impact_pct * scale


def apply_mods(
    baseline: float,
    category_ids: list[str],
    cpu_tier: str,
    gpu_tier: str,
    ram_tier: str,
) -> float:
    """Apply a set of mod categories to a baseline FPS, multiplicatively."""
    multiplier = 1.0
    for cat_id in category_ids:
        impact = mod_effective_impact(cat_id, cpu_tier, gpu_tier)
        multiplier *= 1.0 - impact

    if category_ids and any(c in _VRAM_SENSITIVE_CATEGORIES for c in category_ids):
        multiplier *= 1.0 - _RAM_STUTTER_PENALTY[ram_tier]

    total_reduction = 1.0 - multiplier
    total_reduction = min(total_reduction, _MAX_TOTAL_REDUCTION)
    return baseline * (1.0 - total_reduction)


CATEGORY_IDS = [c.id for c in MOD_CATEGORIES]
FEATURE_COLUMNS = [
    "game",
    "cpu_rank",
    "gpu_rank",
    "resolution_rank",
    "ram_rank",
    *[f"count_{c}" for c in CATEGORY_IDS],
    "total_mod_count",
]


def _rank(order: list[str], value: str) -> int:
    return order.index(value)


def build_feature_row(
    game_id: str,
    cpu_tier: str,
    gpu_tier: str,
    resolution: str,
    ram_tier: str,
    category_ids: list[str],
) -> dict:
    counts = {f"count_{c}": category_ids.count(c) for c in CATEGORY_IDS}
    return {
        "game": game_id,
        "cpu_rank": _rank(CPU_ORDER, cpu_tier),
        "gpu_rank": _rank(GPU_ORDER, gpu_tier),
        "resolution_rank": _rank(RES_ORDER, resolution),
        "ram_rank": _rank(RAM_ORDER, ram_tier),
        **counts,
        "total_mod_count": len(category_ids),
    }


def generate_training_data(
    samples_per_combo: int = 6,
    max_mods: int = 4,
    noise_pct: float = 0.035,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate the synthetic training set described in the module docstring.

    For every game x CPU tier x GPU tier x resolution x RAM tier combination,
    this emits one clean baseline (no-mod) row, plus `samples_per_combo`
    additional rows with a random subset of mod categories applied, each with
    a small amount of random noise added to the resulting FPS to stand in for
    real-world run-to-run variance.
    """
    rng = random.Random(seed)
    rows: list[dict] = []

    for game in GAMES:
        for cpu_tier in CPU_ORDER:
            for gpu_tier in GPU_ORDER:
                for resolution in RES_ORDER:
                    for ram_tier in RAM_ORDER:
                        base = baseline_fps(game.id, cpu_tier, gpu_tier, resolution)

                        # Clean baseline row, no mods.
                        row = build_feature_row(
                            game.id, cpu_tier, gpu_tier, resolution, ram_tier, []
                        )
                        row["fps"] = round(base, 1)
                        rows.append(row)

                        for _ in range(samples_per_combo):
                            n_mods = rng.randint(1, max_mods)
                            categories = rng.sample(
                                CATEGORY_IDS, k=min(n_mods, len(CATEGORY_IDS))
                            )
                            fps = apply_mods(base, categories, cpu_tier, gpu_tier, ram_tier)
                            noise = rng.uniform(-noise_pct, noise_pct)
                            fps = max(fps * (1 + noise), 3.0)

                            row = build_feature_row(
                                game.id, cpu_tier, gpu_tier, resolution, ram_tier, categories
                            )
                            row["fps"] = round(fps, 1)
                            rows.append(row)

    return pd.DataFrame(rows)
