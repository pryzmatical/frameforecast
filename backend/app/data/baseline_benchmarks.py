"""Hand-curated baseline (no-mod) FPS figures for each game.

These are *approximate, representative* numbers informed by publicly available
benchmark trends for each game (the kind of GPU/CPU tier comparisons and
resolution-scaling ratios published by outlets like TechPowerUp or
GamersNexus, and community benchmark threads for older titles), not scraped
figures and not exact reproductions of any specific article or table. They're
meant to be directionally realistic, not precise. See docs/METHODOLOGY.md for
the full explanation and caveats.

Each game defines a reference FPS at a reference hardware point, plus
multipliers for how much CPU tier, GPU tier, and resolution move FPS away
from that reference. The multipliers reflect each game's real-world
performance character:

- Cyberpunk 2077: heavily GPU-bound, resolution scales it hard, CPU matters
  less except at the very high end where a weak CPU can cap a fast GPU.
- Skyrim Special Edition: an older, mostly single-thread-CPU-bound engine.
  GPU headroom matters much more once graphics mods are involved than it
  does vanilla. (Note: the vanilla engine is also famous for physics/engine
  instability well above 60 FPS, which is why many players cap it there
  regardless of how much hardware headroom they have -- this model reports
  the underlying uncapped estimate, not a capped one.)
- Minecraft Java: vanilla rendering is CPU-bound and cheap; GPU only becomes
  the bottleneck once a shader pack is added (modeled in dataset.py's mod
  impact logic, not here).
"""

from __future__ import annotations

from dataclasses import dataclass

CPU_ORDER = ["cpu_entry", "cpu_mid", "cpu_high"]
GPU_ORDER = ["gpu_entry", "gpu_mid", "gpu_upper_mid", "gpu_high", "gpu_enthusiast"]
RES_ORDER = ["1080p", "1440p", "4k"]


@dataclass(frozen=True)
class GameProfile:
    reference_fps: float  # FPS at cpu_mid, gpu_upper_mid, 1080p
    gpu_multiplier: dict[str, float]
    cpu_multiplier: dict[str, dict[str, float]]  # keyed by resolution, then cpu tier
    resolution_multiplier: dict[str, float]


GAME_PROFILES: dict[str, GameProfile] = {
    "cyberpunk_2077": GameProfile(
        reference_fps=92.0,  # gpu_upper_mid / cpu_mid / 1080p, high settings, RT off
        gpu_multiplier={
            "gpu_entry": 0.49,
            "gpu_mid": 0.71,
            "gpu_upper_mid": 1.00,
            "gpu_high": 1.36,
            "gpu_enthusiast": 1.63,
        },
        # Mostly GPU-bound; weak CPUs cost more at low resolution where the
        # GPU isn't the limiter, and cost almost nothing at 4K where it is.
        cpu_multiplier={
            "1080p": {"cpu_entry": 0.88, "cpu_mid": 1.00, "cpu_high": 1.06},
            "1440p": {"cpu_entry": 0.92, "cpu_mid": 1.00, "cpu_high": 1.03},
            "4k": {"cpu_entry": 0.97, "cpu_mid": 1.00, "cpu_high": 1.01},
        },
        resolution_multiplier={"1080p": 1.00, "1440p": 0.74, "4k": 0.40},
    ),
    "skyrim_se": GameProfile(
        reference_fps=105.0,  # gpu_upper_mid / cpu_mid / 1080p, uncapped, high settings
        # Skyrim SE is CPU-bound first; GPU tier matters less vanilla and a
        # lot more once graphics mods are added (see dataset.py).
        gpu_multiplier={
            "gpu_entry": 0.72,
            "gpu_mid": 0.88,
            "gpu_upper_mid": 1.00,
            "gpu_high": 1.10,
            "gpu_enthusiast": 1.16,
        },
        cpu_multiplier={
            "1080p": {"cpu_entry": 0.71, "cpu_mid": 1.00, "cpu_high": 1.33},
            "1440p": {"cpu_entry": 0.74, "cpu_mid": 1.00, "cpu_high": 1.28},
            "4k": {"cpu_entry": 0.80, "cpu_mid": 1.00, "cpu_high": 1.18},
        },
        resolution_multiplier={"1080p": 1.00, "1440p": 0.82, "4k": 0.55},
    ),
    "minecraft_java": GameProfile(
        reference_fps=180.0,  # gpu_upper_mid / cpu_mid / 1080p, vanilla, render distance 12
        # Vanilla rendering barely taxes the GPU; the gap between GPU tiers
        # is small until a shader pack is added.
        gpu_multiplier={
            "gpu_entry": 0.83,
            "gpu_mid": 0.94,
            "gpu_upper_mid": 1.00,
            "gpu_high": 1.04,
            "gpu_enthusiast": 1.07,
        },
        cpu_multiplier={
            "1080p": {"cpu_entry": 0.55, "cpu_mid": 1.00, "cpu_high": 1.48},
            "1440p": {"cpu_entry": 0.58, "cpu_mid": 1.00, "cpu_high": 1.44},
            "4k": {"cpu_entry": 0.63, "cpu_mid": 1.00, "cpu_high": 1.36},
        },
        resolution_multiplier={"1080p": 1.00, "1440p": 0.93, "4k": 0.80},
    ),
}


def baseline_fps(game_id: str, cpu_tier: str, gpu_tier: str, resolution: str) -> float:
    """No-mod estimated average FPS for a hardware + resolution combination."""
    profile = GAME_PROFILES[game_id]
    cpu_mult = profile.cpu_multiplier[resolution][cpu_tier]
    gpu_mult = profile.gpu_multiplier[gpu_tier]
    res_mult = profile.resolution_multiplier[resolution]
    return profile.reference_fps * cpu_mult * gpu_mult * res_mult
