"""Train the weak-label bad-round classifier from exported feature CSVs."""

from __future__ import annotations

from pathlib import Path
import warnings

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIR = PROJECT_ROOT / "data" / "features"
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
LABEL_COLUMN = "bad_round"
LEAKAGE_COLUMNS = {
    "risk_score",
    "bad_round",
    "bad_round_prediction",
    "bad_round_probability",
    "label",
    "target",
    "weak_label",
    "derived_label",
}
BOOLEAN_FEATURES = [
    "survived_round",
    "died_first",
    "opening_kill",
    "opening_death",
    "clutch_situation",
    "survived_after_first_kill",
    "round_win",
]


def load_feature_csvs(feature_dir: Path = FEATURE_DIR) -> pd.DataFrame:
    """Load and combine every exported feature CSV in the data directory."""
    csv_paths = sorted(path for path in feature_dir.glob("*.csv") if path.is_file())
    if not csv_paths:
        raise FileNotFoundError(f"No feature CSV files found in {feature_dir}")

    frames = []
    for csv_path in csv_paths:
        frame = pd.read_csv(csv_path)
        frame["source_csv"] = csv_path.name
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


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


def _heuristic_bad_round_labels(df: pd.DataFrame) -> pd.Series:
    empty = pd.Series(None, index=df.index)
    kills = pd.to_numeric(df.get("kills", empty), errors="coerce").fillna(0)
    deaths = pd.to_numeric(df.get("deaths", empty), errors="coerce").fillna(0)
    utility_count = pd.to_numeric(df.get("utility_count", empty), errors="coerce").fillna(0)

    died_first = df.get("died_first", pd.Series(False, index=df.index)).map(_boolean_to_number).fillna(0)
    opening_death = df.get("opening_death", pd.Series(False, index=df.index)).map(_boolean_to_number).fillna(0)
    opening_kill = df.get("opening_kill", pd.Series(False, index=df.index)).map(_boolean_to_number).fillna(0)
    survived_round = df.get("survived_round", pd.Series(False, index=df.index)).map(_boolean_to_number).fillna(0)
    round_win = df.get("round_win", pd.Series(True, index=df.index)).map(_boolean_to_number).fillna(1)

    return (
        ((deaths >= 1) & (kills == 0))
        | (died_first == 1)
        | (opening_death == 1)
        | ((opening_kill == 0) & (deaths >= 1) & (kills == 0))
        | ((survived_round == 0) & (utility_count == 0))
        | ((round_win == 0) & (deaths >= 1) & (kills == 0))
    ).astype(int)


def add_weak_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the weak target label.

    If risk_score exists, it is treated as the current baseline teacher signal.
    Missing risk_score values fall back to simple heuristics from real features.
    risk_score is not used as a model input to avoid training directly on its own
    generated label.
    """
    labeled = df.copy()
    heuristic_labels = _heuristic_bad_round_labels(labeled)

    if "risk_score" in labeled.columns:
        risk_score = pd.to_numeric(labeled["risk_score"], errors="coerce")
        labeled["bad_round"] = (risk_score >= 0.65).astype("Int64")
        labeled.loc[risk_score.isna(), "bad_round"] = heuristic_labels[risk_score.isna()]
    else:
        labeled["bad_round"] = heuristic_labels

    labeled[LABEL_COLUMN] = labeled[LABEL_COLUMN].astype(int)
    return labeled


def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Build model inputs while explicitly excluding label/leakage columns."""
    prepared = df.copy()

    for column in MODEL_FEATURES:
        if column not in prepared.columns:
            prepared[column] = None

    for column in BOOLEAN_FEATURES:
        prepared[column] = prepared[column].map(_boolean_to_number)

    for column in NUMERIC_FEATURES:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0)

    for column in CATEGORICAL_FEATURES:
        prepared[column] = prepared[column].fillna("unknown").astype(str)

    x = prepared[MODEL_FEATURES]
    y = prepared[LABEL_COLUMN]
    verify_no_label_leakage(x)
    return x, y


def verify_no_label_leakage(x: pd.DataFrame) -> None:
    """Fail fast if label-derived fields accidentally enter the feature matrix."""
    leaking_columns = sorted(LEAKAGE_COLUMNS.intersection(x.columns))
    if leaking_columns:
        raise ValueError(f"Label leakage detected in training features: {leaking_columns}")


def print_training_audit(x: pd.DataFrame, y: pd.Series) -> None:
    print("Training feature columns:")
    for column in x.columns:
        print(f"- {column}")
    print(f"Label column: {LABEL_COLUMN}")
    print(f"Leakage columns excluded from X_train: {sorted(LEAKAGE_COLUMNS)}")
    print(f"Verified leakage columns present in X_train: {sorted(LEAKAGE_COLUMNS.intersection(x.columns))}")

    numeric_x = x.copy()
    for column in BOOLEAN_FEATURES:
        if column in numeric_x.columns:
            numeric_x[column] = numeric_x[column].map(_boolean_to_number)
    for column in numeric_x.columns:
        numeric_x[column] = pd.to_numeric(numeric_x[column], errors="coerce")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        correlations = numeric_x.corrwith(y).dropna().sort_values(key=lambda values: values.abs(), ascending=False)
    print("Top label correlations:")
    if correlations.empty:
        print("- no numeric correlations available")
    else:
        for feature, correlation in correlations.head(15).items():
            print(f"- {feature}: {correlation:.3f}")


def build_model() -> Pipeline:
    """Create the preprocessing and Random Forest pipeline used for training."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def print_top_feature_importances(model: Pipeline, top_n: int = 15) -> None:
    """Print the strongest feature importances from the trained classifier."""
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    feature_names = preprocessor.get_feature_names_out()
    importances = classifier.feature_importances_
    importance_rows = sorted(
        zip(feature_names, importances, strict=True),
        key=lambda item: item[1],
        reverse=True,
    )

    print(f"Top {top_n} feature importances:")
    for feature_name, importance in importance_rows[:top_n]:
        print(f"- {feature_name}: {importance:.4f}")


def split_dataset(
    x: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    if len(x) < 2:
        raise ValueError("Need at least 2 rows to train and evaluate a model.")

    class_counts = y.value_counts()
    stratify = y if len(class_counts) > 1 and class_counts.min() >= 2 else None

    return train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )


def main() -> None:
    """Train, evaluate, audit, and save the bad-round model artifact."""
    df = load_feature_csvs()
    df = add_weak_labels(df)
    x, y = prepare_features(df)
    print_training_audit(x, y)

    x_train, x_test, y_train, y_test = split_dataset(x, y)
    verify_no_label_leakage(x_train)
    model = build_model()
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Loaded rows: {len(df)}")
    print(f"Training rows: {len(x_train)}")
    print(f"Test rows: {len(x_test)}")
    print(f"Bad rounds: {int(y.sum())}")
    print(f"Good rounds: {int((y == 0).sum())}")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print("Note: metrics are against weak labels, so they can be optimistic until real labels are added.")
    print_top_feature_importances(model)
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
