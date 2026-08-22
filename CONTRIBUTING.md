# Contributing

Thanks for looking at FrameForecast. It's a portfolio project built out of
genuine interest in the subject, and if you want to add a game, fix
something, or extend the model, contributions are welcome. Read
[docs/METHODOLOGY.md](docs/METHODOLOGY.md) first if you haven't -- it
explains exactly what this tool does and doesn't claim to do, and that
framing matters for any change you make here.

## Getting set up

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The trained model is already checked in at
`app/models/frameforecast_model.joblib`, so you don't need to retrain it
just to run the API. See "Changing the training data" below for when you
would.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # only needed if the API isn't on localhost:8000
npm run dev
```

## Running tests

```bash
# backend
cd backend && pytest

# frontend
cd frontend && npm test
```

## Before you open a PR

This repo has two independent CI jobs (backend, frontend) -- run the same
checks locally:

```bash
# backend
cd backend
pip install ruff && ruff check .
pytest

# frontend
cd frontend
npm run lint
npm run build   # runs tsc -b, so this is also the typecheck
npm test
```

## Adding a game or mod

The catalog is hand-curated, not scraped or user-submitted, on purpose --
see the Methodology doc for why. If you want to propose a new game or mod:

1. Add the game/mod entry in `backend/app/data/catalog.py` and, for a new
   game, a baseline benchmark profile in
   `backend/app/data/baseline_benchmarks.py` following the existing games'
   pattern (reference FPS at a reference hardware point, plus CPU/GPU/
   resolution multipliers reflecting the game's actual performance
   character -- GPU-bound vs. CPU-bound, etc.).
2. Regenerate the training set and retrain:
   ```bash
   cd backend
   python -m app.ml.train_model
   ```
   This overwrites `app/models/frameforecast_model.joblib` -- commit the
   updated artifact along with your data change.
3. Add or update tests in `backend/tests/` covering the new catalog
   entries, and update `docs/METHODOLOGY.md` with the reasoning behind
   whatever numbers you chose, the same way the existing three games are
   documented there. A new game or mod without documented reasoning behind
   its weights won't be a good fit for this repo -- the whole point is
   that every number is explainable, not just plausible-looking.

## Code style

Backend: [ruff](https://docs.astral.sh/ruff/) with its default rule set,
no project-specific config. Frontend: [oxlint](https://oxc.rs/), also
default config.

## Opening a PR

Keep PRs small and focused. If you're proposing something bigger --
a new game, a different model type, an accuracy improvement -- opening an
issue first to talk through the approach (and, for a new game, the
benchmark sourcing) saves rework on both ends.
