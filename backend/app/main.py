"""FastAPI entrypoint.

Run with: uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import catalog, predict

app = FastAPI(
    title="FrameForecast API",
    description=(
        "Predicts an estimated FPS range for a hardware + game + mod-selection "
        "combination, using a small RandomForestRegressor trained on a "
        "hand-curated dataset. Not a simulation or measurement of real "
        "gameplay -- see /methodology in the frontend app."
    ),
    version="1.0.0",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(predict.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
