# FrameForecast

A calculator that takes your PC specs, a game, and a set of mods you're
considering, and returns an **estimated** FPS range from a small model
trained on a hand-curated dataset.

## Why this exists

My other public repos ([BriefGenerator](https://github.com/pryzmatical/BriefGenerator),
[OpsDesk](https://github.com/pryzmatical/OpsDesk), [WebhookRelay](https://github.com/pryzmatical/WebhookRelay))
are all built around patterns I use professionally. This one isn't -- I
built it out of genuine personal interest in PC hardware and modding, and
used it as an excuse to build a small, honest applied-ML feature end to end:
curated training data, a documented feature/impact model, a scikit-learn
regression pipeline, an inference API, and a results UI that surfaces
uncertainty and interpretability instead of hiding them. It also connects to
the dashboard/BI side of my background: the feature-importance chart on the
results page is the same "what's actually driving this number" instinct
that shows up in reporting work, just applied to FPS instead of business
metrics.

**Read this before anything else:** [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
explains exactly what this tool does and doesn't do. Short version:
real game and mod performance depends on engine internals, shader
compilation, driver behavior, and mod interactions that no offline tool can
compute. FrameForecast does not simulate or measure gameplay. It returns a
statistical **estimate** from a model trained on a small, documented,
hand-curated dataset, and every surface in this app (API responses, the
results page, this README) is written to say so.

## Architecture

```
React + Vite + TS frontend  --HTTP-->  FastAPI backend  -->  scikit-learn
  (form, results, charts)              (validation,          RandomForestRegressor
                                         catalog data)         (loaded from a
                                                                 checked-in
                                                                 .joblib artifact)
```

- **Data layer** (`backend/app/data/`): hand-curated games, hardware tiers,
  and a mod library tagged by category (texture overhaul, graphics/shader
  overhaul, script-heavy gameplay, etc.), each with a researched or
  reasonably-estimated performance-impact weight.
- **Training data** (`backend/app/ml/dataset.py`): synthesizes ~2,800
  training rows by combining curated baseline hardware benchmarks with a
  documented, deterministic mod-impact model and a bit of random noise. See
  the Methodology doc for exactly how and why.
- **Model** (`backend/app/ml/train_model.py`, `model.py`): a
  `RandomForestRegressor` in a scikit-learn `Pipeline`. The predicted range
  shown to the user comes from the spread of predictions across the
  forest's individual trees (a genuine, if simplified, model-native
  uncertainty measure), and the feature-importance breakdown comes straight
  from `feature_importances_`, grouped into readable categories.
- **API** (`backend/app/routers/`): `GET /catalog`, `GET /games/{id}/mods`,
  and `POST /predict`. Stateless -- no accounts, no database, every request
  is independent.
- **Frontend** (`frontend/src/`): a form (game, hardware tiers, resolution,
  mod multi-select) -> results view with the FPS estimate, a range chart,
  and a feature-importance chart (Recharts), plus a Methodology page with
  the full explanation and the trademark/non-affiliation disclaimer.

## What's in the training set

Three games were chosen for having large modding communities and enough
publicly known benchmark context to build a plausible baseline: **The
Elder Scrolls V: Skyrim Special Edition**, **Cyberpunk 2077**, and
**Minecraft (Java Edition)**. Hardware is modeled as 3 CPU tiers, 5 GPU
tiers, 3 RAM tiers, and 3 resolutions (1080p/1440p/4K) -- coarse on purpose,
so the model has a small, defensible feature space instead of thousands of
near-duplicate part SKUs.

Baseline (no-mod) FPS figures are approximate, representative numbers
informed by publicly available benchmark trends for these games (the kind
of GPU/CPU tier comparisons and resolution-scaling ratios published by
outlets like TechPowerUp or GamersNexus, and community benchmark threads for
older titles) -- not scraped from, and not an exact reproduction of, any one
source. Mods are tagged into six impact categories (texture overhaul,
graphics/shader overhaul, lighting/weather overhaul, script-heavy gameplay,
NPC/creature density overhaul, lightweight tweak), each with a
reasonably-estimated FPS impact weight that scales with whichever hardware
tier it's most sensitive to. Full detail, including the exact weights and
the reasoning behind each game's performance profile, is in
[docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Quickstart

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env

# The trained model is already checked in at app/models/frameforecast_model.joblib.
# To retrain from scratch (regenerates the synthetic training set too):
python -m app.ml.train_model

uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000` (interactive docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # only needed if the API isn't on localhost:8000
npm run dev
```

Visit `http://localhost:5173`.

## Testing

```bash
# backend
cd backend && pytest

# frontend
cd frontend && npm test
```

Backend coverage (`backend/tests/`):

- `/catalog` and `/games/{id}/mods` return the expected games, hardware
  tiers, and per-game mod lists, and 404 on an unknown game
  (`test_catalog.py`)
- `/predict` on valid input returns a coherent low/predicted/high range and
  a non-empty feature-importance breakdown that sums to ~1
  (`test_predict.py`)
- `/predict` rejects unknown/out-of-range hardware values, a mod from the
  wrong game, and an unknown mod ID with 422s (`test_predict.py`)
- `/predict` returns a 503 with a clear message if the model artifact isn't
  loaded, instead of a raw crash (`test_predict.py`)
- Dataset generation shape/bounds and direct model-loading behavior,
  independent of the HTTP layer (`test_model.py`)

Frontend coverage (`frontend/src/tests/`): the `api.ts` client's success,
error, and network-failure handling; the calculator form's client-side
validation and happy path end to end against a mocked API; the catalog-load
error banner; and render smoke tests for both charts.

Not tested: the training script itself isn't run in CI/tests (it's a
one-time/on-demand build step, not request-path code), and there's no
end-to-end browser test across the real backend + frontend together.

## What's not implemented

- No accounts or saved history -- this is a stateless calculator, by design
- No real per-mod benchmarking (see Methodology -- this is a category-based
  estimate, not a claim about any specific mod)

## Trademark and affiliation notice

FrameForecast is not affiliated with, endorsed by, or sponsored by any game
publisher or developer, any GPU/CPU vendor, or any mod author or modding
platform referenced in this project. NVIDIA, AMD, and Intel are trademarks
of their respective owners, as are the game titles referenced here (The
Elder Scrolls V: Skyrim Special Edition, Cyberpunk 2077, Minecraft).

## License

MIT. See [LICENSE](LICENSE).
