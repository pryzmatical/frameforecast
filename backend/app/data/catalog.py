"""Static reference data: supported games, hardware tiers, and the mod library.

Everything here is hand-curated for this portfolio project. Hardware tiers are
deliberately coarse (three CPU tiers, five GPU tiers) rather than an exhaustive
part database, so the model has a small, defensible feature space instead of
thousands of near-duplicate SKUs. See docs/METHODOLOGY.md for how the example
part names were chosen and how baseline FPS figures were sourced.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    id: str
    label: str
    example_parts: str
    rank: int  # ordinal position, used as a numeric feature for the model


@dataclass(frozen=True)
class Game:
    id: str
    name: str
    short_description: str


@dataclass(frozen=True)
class ModCategory:
    id: str
    label: str
    description: str
    base_impact_pct: float  # fraction of FPS lost at reference hardware, e.g. 0.08 = 8%
    sensitivity: str  # "gpu", "cpu", or "none" -- which hardware tier scales the impact


@dataclass(frozen=True)
class Mod:
    id: str
    name: str
    category_id: str
    game_id: str
    note: str = ""


# ---------------------------------------------------------------------------
# Hardware tiers
# ---------------------------------------------------------------------------

CPU_TIERS: list[Tier] = [
    Tier("cpu_entry", "Entry", "e.g. Ryzen 5 3600 / Core i5-10400", 0),
    Tier("cpu_mid", "Mid-range", "e.g. Ryzen 5 7600 / Core i5-13600K", 1),
    Tier("cpu_high", "High-end", "e.g. Ryzen 7 7800X3D / Core i7-14700K", 2),
]

GPU_TIERS: list[Tier] = [
    Tier("gpu_entry", "Entry", "e.g. RTX 3050 / RX 6600", 0),
    Tier("gpu_mid", "Mid-range", "e.g. RTX 4060 / RX 7600", 1),
    Tier("gpu_upper_mid", "Upper-mid", "e.g. RTX 4070 / RX 7800 XT", 2),
    Tier("gpu_high", "High-end", "e.g. RTX 4080 Super / RX 7900 XTX", 3),
    Tier("gpu_enthusiast", "Enthusiast", "e.g. RTX 4090", 4),
]

RAM_TIERS: list[Tier] = [
    Tier("ram_8", "8 GB", "8 GB system memory", 0),
    Tier("ram_16", "16 GB", "16 GB system memory", 1),
    Tier("ram_32", "32 GB+", "32 GB or more system memory", 2),
]

RESOLUTIONS: list[Tier] = [
    Tier("1080p", "1920x1080", "1080p / Full HD", 0),
    Tier("1440p", "2560x1440", "1440p / QHD", 1),
    Tier("4k", "3840x2160", "4K / UHD", 2),
]

_TIER_LOOKUP: dict[str, Tier] = {
    t.id: t for group in (CPU_TIERS, GPU_TIERS, RAM_TIERS, RESOLUTIONS) for t in group
}


def get_tier(tier_id: str) -> Tier | None:
    return _TIER_LOOKUP.get(tier_id)


# ---------------------------------------------------------------------------
# Games
# ---------------------------------------------------------------------------

GAMES: list[Game] = [
    Game(
        "skyrim_se",
        "The Elder Scrolls V: Skyrim Special Edition",
        "Open-world RPG with one of the largest modding ecosystems of any game.",
    ),
    Game(
        "cyberpunk_2077",
        "Cyberpunk 2077",
        "GPU-heavy open-world action RPG, popular for visual and gameplay overhaul mods.",
    ),
    Game(
        "minecraft_java",
        "Minecraft (Java Edition)",
        "Single-thread-CPU-bound base game whose look changes completely with shader packs.",
    ),
]

_GAME_LOOKUP = {g.id: g for g in GAMES}


def get_game(game_id: str) -> Game | None:
    return _GAME_LOOKUP.get(game_id)


# ---------------------------------------------------------------------------
# Mod categories
#
# base_impact_pct is the estimated fraction of FPS lost at "reference"
# hardware (upper-mid GPU, mid CPU) from a single mod in that category.
# sensitivity controls which tier the impact gets scaled by in
# app/ml/dataset.py -- weaker hardware feels a GPU- or CPU-sensitive mod
# more than the reference tier does.
# ---------------------------------------------------------------------------

MOD_CATEGORIES: list[ModCategory] = [
    ModCategory(
        "lightweight_tweak",
        "Lightweight tweak",
        "UI, quality-of-life, or config-only changes with no meaningful rendering or "
        "simulation cost (e.g. inventory sorting, HUD tweaks).",
        base_impact_pct=0.02,
        sensitivity="none",
    ),
    ModCategory(
        "texture_overhaul",
        "Texture overhaul",
        "Higher-resolution textures for the world, characters, or objects. Mostly a "
        "VRAM/streaming cost, so it hits harder on weaker GPUs and at higher resolutions.",
        base_impact_pct=0.08,
        sensitivity="gpu",
    ),
    ModCategory(
        "graphics_overhaul",
        "Graphics/shader overhaul",
        "ENB, ReShade, or full shader-pipeline replacements (e.g. Minecraft shader packs). "
        "The single biggest FPS cost category in this model.",
        base_impact_pct=0.30,
        sensitivity="gpu",
    ),
    ModCategory(
        "lighting_overhaul",
        "Lighting/weather overhaul",
        "Dynamic lighting, volumetrics, or weather systems that don't replace the whole "
        "shader pipeline but add real-time rendering cost.",
        base_impact_pct=0.16,
        sensitivity="gpu",
    ),
    ModCategory(
        "script_heavy_gameplay",
        "Script-heavy gameplay",
        "Combat, needs/survival, or systemic overhauls that run additional logic every "
        "frame or tick. Mostly a CPU cost.",
        base_impact_pct=0.12,
        sensitivity="cpu",
    ),
    ModCategory(
        "npc_creature_overhaul",
        "NPC/creature density overhaul",
        "More NPCs, more spawns, or busier AI. Scales with CPU headroom.",
        base_impact_pct=0.15,
        sensitivity="cpu",
    ),
]

_MOD_CATEGORY_LOOKUP = {c.id: c for c in MOD_CATEGORIES}


def get_mod_category(category_id: str) -> ModCategory | None:
    return _MOD_CATEGORY_LOOKUP.get(category_id)


# ---------------------------------------------------------------------------
# Mod library (per game)
#
# These are named as recognizable *examples* of each category so the form
# reads naturally -- they are illustrative labels, not benchmarks of any
# specific real mod. FrameForecast estimates by category weight, not by
# measuring the named mod itself. See docs/METHODOLOGY.md.
# ---------------------------------------------------------------------------

MODS: list[Mod] = [
    # Skyrim SE
    Mod("skyrim_2k_textures", "2K/4K texture overhaul pack", "texture_overhaul", "skyrim_se"),
    Mod("skyrim_enb", "ENB graphics overhaul", "graphics_overhaul", "skyrim_se"),
    Mod("skyrim_lighting", "Dynamic lighting/weather overhaul", "lighting_overhaul", "skyrim_se"),
    Mod("skyrim_combat_overhaul", "Script-heavy combat overhaul", "script_heavy_gameplay", "skyrim_se"),
    Mod("skyrim_npc_overhaul", "Immersive NPC/creature density overhaul", "npc_creature_overhaul", "skyrim_se"),
    Mod("skyrim_ui_tweak", "UI and inventory tweaks", "lightweight_tweak", "skyrim_se"),

    # Cyberpunk 2077
    Mod("cp77_texture_pack", "4K texture and material pack", "texture_overhaul", "cyberpunk_2077"),
    Mod("cp77_reshade", "ReShade visual overhaul", "graphics_overhaul", "cyberpunk_2077"),
    Mod("cp77_lighting", "Volumetric lighting/weather overhaul", "lighting_overhaul", "cyberpunk_2077"),
    Mod("cp77_gameplay_overhaul", "Systemic gameplay/AI overhaul", "script_heavy_gameplay", "cyberpunk_2077"),
    Mod("cp77_crowd_density", "NPC/crowd density overhaul", "npc_creature_overhaul", "cyberpunk_2077"),
    Mod("cp77_hud_tweak", "HUD and minimap tweaks", "lightweight_tweak", "cyberpunk_2077"),

    # Minecraft Java
    Mod("mc_resource_pack", "High-resolution resource pack", "texture_overhaul", "minecraft_java"),
    Mod("mc_shader_pack", "Shader pack (path-traced style lighting)", "graphics_overhaul", "minecraft_java"),
    Mod("mc_dynamic_lights", "Dynamic lights and weather mod", "lighting_overhaul", "minecraft_java"),
    Mod("mc_tech_mod", "Script-heavy tech/automation mod", "script_heavy_gameplay", "minecraft_java"),
    Mod("mc_mob_overhaul", "Mob/creature density overhaul", "npc_creature_overhaul", "minecraft_java"),
    Mod("mc_hud_tweak", "Inventory/HUD quality-of-life mod", "lightweight_tweak", "minecraft_java"),
]


def mods_for_game(game_id: str) -> list[Mod]:
    return [m for m in MODS if m.game_id == game_id]


_MOD_LOOKUP = {m.id: m for m in MODS}


def get_mod(mod_id: str) -> Mod | None:
    return _MOD_LOOKUP.get(mod_id)
