from __future__ import annotations

from statistics import mean
from typing import Any

from app.features import summarize_missing_features


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def calculate_baseline_risk(round_features: dict[str, Any]) -> float:
    """
    Baseline placeholder risk score using only real extracted feature values.

    This is intentionally simple until a trained scikit-learn model is added.
    Missing values do not contribute to the score.
    """
    risk = 0.20

    deaths = round_features.get("deaths")
    kills = round_features.get("kills")
    utility_count = round_features.get("utility_count")
    died_first = round_features.get("died_first")
    survived_round = round_features.get("survived_round")

    if deaths == 1:
        risk += 0.25
    elif isinstance(deaths, int) and deaths > 1:
        risk += 0.30

    if kills == 0:
        risk += 0.20

    if utility_count == 0:
        risk += 0.20

    if died_first is True:
        risk += 0.20

    if survived_round is True:
        risk -= 0.15

    return round(_clamp(risk), 2)


def _detected_issues(round_features: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    if round_features.get("utility_count") == 0:
        issues.append("No utility used")

    if round_features.get("deaths") == 1 and round_features.get("kills") == 0:
        issues.append("Died without a kill")

    if round_features.get("died_first") is True:
        issues.append("First death of the round")

    if round_features.get("damage_dealt") == 0 and round_features.get("kills") == 0:
        issues.append("No damage or kills recorded")

    return issues


def build_report(
    features: list[dict[str, Any]],
    predictions: list[dict[str, Any]] | None = None,
    model_status: str = "baseline_used",
) -> dict[str, Any]:
    if not features:
        raise ValueError("No round features were supplied to build_report.")

    player_name = str(features[0].get("player_name", ""))
    round_reports = []
    risk_scores = []
    predictions = predictions or []

    for index, row in enumerate(features):
        risk_score = calculate_baseline_risk(row)
        risk_scores.append(risk_score)
        prediction = predictions[index] if index < len(predictions) else {}
        round_report = {
            "round": row.get("round"),
            "risk_score": risk_score,
            "bad_round_prediction": prediction.get("bad_round_prediction"),
            "bad_round_probability": prediction.get("bad_round_probability"),
            "detected_issues": _detected_issues(row),
            "raw_features": row,
        }
        round_reports.append(round_report)

    return {
        "player": player_name,
        "rounds_analyzed": len(features),
        "overall_risk_score": round(mean(risk_scores), 2) if risk_scores else None,
        "model_status": model_status,
        "round_reports": round_reports,
        "missing_features_summary": summarize_missing_features(features),
    }
