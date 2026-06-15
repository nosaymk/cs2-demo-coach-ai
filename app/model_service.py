"""Model loading and inference helpers for the FastAPI app."""

from __future__ import annotations

from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "bad_round_model.pkl"

NUMERIC_FEATURES = [
    "round",
    "kills",
    "deaths",
    "damage_dealt",
    "flashes_thrown",
    "smokes_thrown",
    "molotovs_incendiaries_thrown",
    "he_grenades_thrown",
    "utility_count",
    "survived_round",
    "died_first",
    "death_tick",
    "death_time",
    "opening_kill",
    "opening_death",
    "kills_before_death",
    "damage_before_death",
    "clutch_situation",
    "survived_after_first_kill",
    "utility_used_before_death",
    "round_win",
    "team_alive_when_player_died",
    "enemies_alive_when_player_died",
]
CATEGORICAL_FEATURES = ["side", "team"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
BOOLEAN_FEATURES = [
    "survived_round",
    "died_first",
    "opening_kill",
    "opening_death",
    "clutch_situation",
    "survived_after_first_kill",
    "round_win",
]


def model_exists() -> bool:
    """Return whether the trained demo model artifact is available."""
    return MODEL_PATH.exists()


def get_model_info() -> dict[str, Any]:
    """Return operational metadata used by `/model-info` and Developer Tools."""
    exists = model_exists()
    info: dict[str, Any] = {
        "model_status": "ml_model_used" if exists else "model_not_found_baseline_used",
        "model_path": str(MODEL_PATH),
        "model_exists": exists,
        "model_type": None,
        "feature_columns": MODEL_FEATURES,
        "last_modified": None,
    }

    if not exists:
        return info

    modified_timestamp = MODEL_PATH.stat().st_mtime
    info["last_modified"] = datetime.fromtimestamp(modified_timestamp, tz=timezone.utc).isoformat()

    try:
        model = load_model()
    except Exception as exc:
        info["model_status"] = "model_load_failed"
        info["model_type"] = None
        info["load_error"] = str(exc)
        return info

    info["model_type"] = type(model).__name__
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        info["feature_columns"] = list(feature_names)

    preprocessor = getattr(model, "named_steps", {}).get("preprocessor") if hasattr(model, "named_steps") else None
    if preprocessor is not None and hasattr(preprocessor, "feature_names_in_"):
        info["feature_columns"] = list(preprocessor.feature_names_in_)

    return info


@lru_cache(maxsize=1)
def load_model() -> Any:
    """Load the scikit-learn pipeline once per process."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def _boolean_to_number(value: object) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return float(value)

    normalized = str(value).strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return 1.0
    if normalized in {"false", "0", "no"}:
        return 0.0
    return None


def _prepare_model_frame(features: list[dict[str, Any]]) -> pd.DataFrame:
    dataframe = pd.DataFrame(features)

    for column in MODEL_FEATURES:
        if column not in dataframe.columns:
            dataframe[column] = None

    for column in BOOLEAN_FEATURES:
        dataframe[column] = dataframe[column].map(_boolean_to_number)

    for column in NUMERIC_FEATURES:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").fillna(0)

    for column in CATEGORICAL_FEATURES:
        dataframe[column] = dataframe[column].fillna("unknown").astype(str)

    return dataframe[MODEL_FEATURES]


def _positive_class_index(model: Any) -> int | None:
    classes = getattr(model, "classes_", None)
    if classes is None:
        return None

    for index, class_value in enumerate(classes):
        if int(class_value) == 1:
            return index
    return None


def predict_bad_round(features: list[dict[str, Any]]) -> list[dict[str, int | float]]:
    """Predict review labels and probabilities for extracted round features."""
    if not features:
        return []

    model = load_model()
    model_input = _prepare_model_frame(features)
    predictions = model.predict(model_input)

    probabilities: list[float]
    if hasattr(model, "predict_proba"):
        probability_matrix = model.predict_proba(model_input)
        positive_index = _positive_class_index(model)
        if positive_index is None:
            probabilities = [float(prediction) for prediction in predictions]
        else:
            probabilities = [float(row[positive_index]) for row in probability_matrix]
    else:
        probabilities = [float(prediction) for prediction in predictions]

    return [
        {
            "bad_round_prediction": int(prediction),
            "bad_round_probability": round(probability, 4),
        }
        for prediction, probability in zip(predictions, probabilities, strict=True)
    ]
