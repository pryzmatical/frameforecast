"""Trains the FrameForecast FPS regression model and writes the artifact.

Run from `backend/`:

    python -m app.ml.train_model

This regenerates the synthetic training set (see dataset.py), fits a
RandomForestRegressor inside a scikit-learn Pipeline (one-hot encoding for
`game`, the rest of the features are already small integer ranks/counts),
prints a quick train/test evaluation, and writes
`app/models/frameforecast_model.joblib`.

RandomForestRegressor was chosen over a single GradientBoostingRegressor for
two portfolio-relevant reasons: `feature_importances_` gives the results page
its "what mattered most" breakdown, and averaging predictions across the
individual trees gives a natural, model-native uncertainty band (see
`model.py`) instead of a made-up +/- percentage.
"""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.ml.dataset import FEATURE_COLUMNS, generate_training_data

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "frameforecast_model.joblib"
MODEL_VERSION = "1.0.0"


def build_pipeline() -> Pipeline:
    numeric_features = [c for c in FEATURE_COLUMNS if c != "game"]
    preprocessor = ColumnTransformer(
        transformers=[
            ("game", OneHotEncoder(handle_unknown="ignore"), ["game"]),
            ("numeric", "passthrough", numeric_features),
        ]
    )
    model = RandomForestRegressor(
        n_estimators=80,
        max_depth=9,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


def main() -> None:
    df = generate_training_data()
    X = df[FEATURE_COLUMNS]
    y = df["fps"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Training rows: {len(df)}")
    print(f"Test MAE: {mae:.2f} FPS")
    print(f"Test R^2: {r2:.3f}")

    # Refit on the full dataset for the shipped artifact.
    pipeline.fit(X, y)

    feature_names = list(
        pipeline.named_steps["preprocess"].get_feature_names_out()
    )
    importances = pipeline.named_steps["model"].feature_importances_

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "feature_columns": FEATURE_COLUMNS,
            "feature_names_out": feature_names,
            "feature_importances": dict(zip(feature_names, importances.tolist())),
            "version": MODEL_VERSION,
            "train_mae": round(float(mae), 2),
            "train_r2": round(float(r2), 3),
            "n_training_rows": int(len(df)),
        },
        MODEL_PATH,
        compress=3,
    )
    print(f"Wrote model artifact to {MODEL_PATH}")


if __name__ == "__main__":
    main()
