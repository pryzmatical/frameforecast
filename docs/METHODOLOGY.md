# Methodology

FrameForecast is a portfolio/demo project. This document explains, in more
detail than the in-app Methodology page, exactly how its FPS estimates are
produced, so nothing here overstates what's actually implemented.

## This is an estimate, not a simulation

Real game and mod performance depends on engine internals, shader
compilation, driver behavior, the specific save file, and mod interactions
that no offline tool can compute from hardware specs alone. FrameForecast
does not run the game, does not measure your hardware, and does not
simulate anything. It returns a statistical estimate from a small regression
model trained on a hand-curated dataset. Every user-facing surface (API
response, results page, this document) says "estimated" or "predicted," and
none of them say "simulates" or "measures."

## Games and hardware tiers

Three games were chosen for having large, well-documented modding
communities and enough publicly available benchmark context to build a
plausible baseline:

- The Elder Scrolls V: Skyrim Special Edition
- Cyberpunk 2077
- Minecraft (Java Edition)

Hardware is modeled as three CPU tiers, five GPU tiers, three RAM tiers, and
three resolutions (1080p/1440p/4K), rather than an exhaustive parts
database. That keeps the feature space small and defensible instead of
implying false precision from thousands of near-duplicate SKUs. See
`backend/app/data/catalog.py` for the exact tier definitions and example
parts used to describe each one.

## How the baseline (no-mod) FPS numbers were built

`backend/app/data/baseline_benchmarks.py` defines, per game, a reference FPS
at a reference hardware point (mid-tier CPU, upper-mid GPU, 1080p) plus
multipliers for how CPU tier, GPU tier, and resolution move FPS away from
that reference. Those multipliers were chosen to reflect each game's known
real-world performance character:

- **Cyberpunk 2077** is heavily GPU-bound; resolution scales it hard, and
  CPU tier matters far less except that weak CPUs can cap a fast GPU at low
  resolution.
- **Skyrim Special Edition** runs on an older, largely single-thread-CPU-bound
  engine. GPU tier matters much more once graphics mods (ENB, etc.) are
  involved than it does vanilla. Note: the vanilla engine is also known for
  physics/animation instability well above 60 FPS, which is why many players
  deliberately cap it there regardless of how much hardware headroom they
  have. This model reports the underlying uncapped estimate, not a
  player-capped one.
- **Minecraft Java** is CPU-bound and cheap to render vanilla; GPU only
  becomes the bottleneck once a shader pack is added, which is handled by
  the mod-impact model below, not the baseline table.

These figures are **approximate and representative**, informed by publicly
available benchmark trends for these games (the kind of GPU/CPU tier
comparisons and resolution-scaling ratios published by outlets like
TechPowerUp or GamersNexus, and community benchmark threads for older
titles). They are not scraped from, and should not be read as an exact
reproduction of, any specific article or benchmark table.

## The mod-impact model

There is no public dataset of controlled, per-mod-combination FPS benchmarks
across every hardware tier, so mod impact is modeled by category rather than
by measuring any specific real mod:

| Category | What it covers | Base FPS impact | Most sensitive to |
| --- | --- | --- | --- |
| Lightweight tweak | UI/config-only changes | ~2% | Nothing in particular |
| Texture overhaul | Higher-res textures | ~8% | GPU tier (and low system RAM) |
| Graphics/shader overhaul | ENB, ReShade, full shader-pipeline replacements | ~30% | GPU tier |
| Lighting/weather overhaul | Dynamic lighting/weather, not a full shader swap | ~16% | GPU tier |
| Script-heavy gameplay | Combat/needs/systemic overhauls | ~12% | CPU tier |
| NPC/creature density overhaul | More spawns, busier AI | ~15% | CPU tier |

Each category's impact is scaled up on weaker hardware in its sensitive
dimension and scaled down on stronger hardware (see
`backend/app/ml/dataset.py::mod_effective_impact`). Multiple mods stack
multiplicatively, capped so a handful of mods can't estimate an implausible
near-zero FPS. Texture/graphics-heavy combinations get an additional penalty
on 8GB RAM configurations, modeling asset-streaming stutter.

Named mods in the app's mod library (e.g. "ENB graphics overhaul") are
**illustrative labels for a category**, not benchmarks of, or claims about,
any specific real mod.

## Building the training set

Training rows are generated (`backend/app/ml/dataset.py::generate_training_data`)
by combining the baseline table and the mod-impact model across every game x
CPU tier x GPU tier x resolution x RAM tier combination, plus randomized mod
selections and a small amount of random noise (+/- ~3.5%) standing in for
real-world run-to-run variance. This produces roughly 2,800 rows: enough for
a small regression model to learn from, while being explicit that it's a
documented, synthesized approximation, not a table of measured results.

## The model

A `RandomForestRegressor` (scikit-learn) is trained on the game, CPU/GPU/RAM
tier ranks, resolution rank, and per-category mod counts, to predict average
FPS. Training and evaluation code is in `backend/app/ml/train_model.py`;
run `python -m app.ml.train_model` from `backend/` to regenerate the dataset
and retrain from scratch. On a held-out 20% split of the current dataset,
the model reports roughly R^2 ~ 0.97 and a mean absolute error of about 5-6
FPS -- a measure of how well it reproduces the deterministic function it was
trained on, not a claim about real-world accuracy.

The predicted range shown in the API and UI comes from the spread of
predictions across the individual trees in the forest: tighter agreement
produces a narrower range, more disagreement produces a wider one. That's a
genuine, if simplified, model-native uncertainty measure rather than an
arbitrary +/- percentage -- but it still only reflects the model's own
internal confidence, not measured real-world variance.

The feature-importance breakdown comes directly from the trained model's
`feature_importances_`, grouped into readable categories (e.g. every
one-hot "game" column rolled into a single "Game" bar).

## What this demonstrates

This project was built out of genuine personal interest in the intersection
of PC hardware, modding, and applied ML, not as a rebuild of a production
pattern from a day job. It's meant to show an end-to-end ML feature: data
curation and documentation, feature engineering, a reproducible training
script with a checked-in artifact, an inference API, and a results UI that
surfaces uncertainty and interpretability instead of hiding them.

## Trademark and affiliation notice

FrameForecast is not affiliated with, endorsed by, or sponsored by any game
publisher or developer, any GPU/CPU vendor, or any mod author or modding
platform referenced in this project. NVIDIA, AMD, and Intel are trademarks
of their respective owners, as are the game titles referenced here (The
Elder Scrolls V: Skyrim Special Edition, Cyberpunk 2077, Minecraft).
