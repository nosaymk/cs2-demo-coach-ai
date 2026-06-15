"""FastAPI entrypoint for upload, analysis, replay, and dataset export routes."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.diagnostics import diagnose_player_positions
from app.features import FeatureExtractionError, PlayerNotFoundError, extract_player_round_features
from app.frontend import INDEX_HTML
from app.model_service import get_model_info, model_exists, predict_bad_round
from app.parser import DemoParseError, parse_demo
from app.replay import extract_replay_data
from app.report import build_report, calculate_baseline_risk
from app.schemas import (
    AnalysisReport,
    FeatureExportResponse,
    HealthResponse,
    ModelInfoResponse,
    PositionDiagnosticResponse,
    ReplayDataResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
FEATURE_DIR = PROJECT_ROOT / "data" / "features"
STATIC_DIR = PROJECT_ROOT / "static"
CSV_COLUMNS = [
    "demo_id",
    "player_name",
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
    "side",
    "team",
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
    "risk_score",
]

app = FastAPI(
    title="CS Demo Coach AI",
    version="0.1.0",
    description="Analyze real Counter-Strike 2 .dem files with Awpy and return player round reports.",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    """Serve the player-facing upload and report frontend."""
    return HTMLResponse(INDEX_HTML)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return a lightweight health check for local and container probes."""
    return HealthResponse()


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> dict[str, Any]:
    """Expose model artifact metadata without running inference."""
    return get_model_info()


def _safe_filename(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    cleaned = "".join(character if character in allowed else "_" for character in value)
    return cleaned.strip("._") or "upload.dem"


def _player_slug(player_name: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    slug = "".join(character if character in allowed else "_" for character in player_name)
    return slug.strip("_") or "player"


async def _save_uploaded_demo(file: UploadFile, player_name: str) -> tuple[Path, str, str]:
    """Validate and persist an uploaded demo for endpoints that require a player."""
    cleaned_player_name = player_name.strip()
    if not cleaned_player_name:
        raise HTTPException(status_code=400, detail="player_name is required and cannot be empty.")

    original_name = file.filename or ""
    if Path(original_name).suffix.lower() != ".dem":
        raise HTTPException(status_code=400, detail="Uploaded file must have a .dem extension.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    demo_id = uuid4().hex
    saved_path = UPLOAD_DIR / f"{demo_id}_{_safe_filename(Path(original_name).name)}"

    try:
        with saved_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)
    finally:
        await file.close()

    return saved_path, cleaned_player_name, demo_id


async def _save_uploaded_dem_file(file: UploadFile) -> Path:
    """Validate and persist an uploaded demo for parser-only diagnostics."""
    original_name = file.filename or ""
    if Path(original_name).suffix.lower() != ".dem":
        raise HTTPException(status_code=400, detail="Uploaded file must have a .dem extension.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    demo_id = uuid4().hex
    saved_path = UPLOAD_DIR / f"{demo_id}_{_safe_filename(Path(original_name).name)}"

    try:
        with saved_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)
    finally:
        await file.close()

    return saved_path


def _parse_demo_for_analysis(saved_path: Path) -> Any:
    """Convert parser exceptions into readable API errors."""
    try:
        return parse_demo(str(saved_path))
    except DemoParseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


def _extract_features_for_player(parsed_demo: Any, player_name: str) -> list[dict[str, Any]]:
    """Convert feature extraction exceptions into endpoint-friendly API errors."""
    try:
        return extract_player_round_features(parsed_demo, player_name)
    except PlayerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FeatureExtractionError as exc:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


def _baseline_predictions(round_features: list[dict[str, Any]]) -> list[dict[str, int | float]]:
    """Build fallback prediction fields from the transparent baseline score."""
    predictions: list[dict[str, int | float]] = []
    for row in round_features:
        risk_score = calculate_baseline_risk(row)
        predictions.append(
            {
                "bad_round_prediction": int(risk_score >= 0.65),
                "bad_round_probability": risk_score,
            }
        )
    return predictions


@app.post("/diagnose-demo", response_model=PositionDiagnosticResponse)
async def diagnose_demo(
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Inspect whether the parsed demo exposes position/tick data."""
    saved_path = await _save_uploaded_dem_file(file)
    parsed_demo = _parse_demo_for_analysis(saved_path)
    diagnostics = diagnose_player_positions(parsed_demo)
    return jsonable_encoder(diagnostics)


@app.post("/replay-data", response_model=ReplayDataResponse)
async def replay_data(
    file: UploadFile = File(...),
    player_name: str | None = Query(default=None, description="Optional player to highlight in the replay viewer."),
) -> dict[str, Any]:
    """Return lightweight replay data extracted from real Awpy tick/event frames."""
    saved_path = await _save_uploaded_dem_file(file)
    parsed_demo = _parse_demo_for_analysis(saved_path)
    replay = extract_replay_data(parsed_demo, selected_player=player_name)
    return jsonable_encoder(replay)


@app.post("/analyze-demo", response_model=AnalysisReport)
async def analyze_demo(
    file: UploadFile = File(...),
    player_name: str = Query(..., description="Exact or case-insensitive in-demo player name."),
) -> dict:
    """Analyze one player from a real demo and return a coaching report."""
    saved_path, cleaned_player_name, _demo_id = await _save_uploaded_demo(file, player_name)
    parsed_demo = _parse_demo_for_analysis(saved_path)
    round_features = _extract_features_for_player(parsed_demo, cleaned_player_name)

    if model_exists():
        predictions = predict_bad_round(round_features)
        model_status = "ml_model_used"
    else:
        predictions = _baseline_predictions(round_features)
        model_status = "model_not_found_baseline_used"

    report = build_report(round_features, predictions=predictions, model_status=model_status)
    return jsonable_encoder(report)


@app.post("/extract-features", response_model=FeatureExportResponse)
async def extract_features(
    file: UploadFile = File(...),
    player_name: str = Query(..., description="Exact or case-insensitive in-demo player name."),
) -> dict:
    """Export extracted per-round player features as a local CSV dataset."""
    saved_path, cleaned_player_name, demo_id = await _save_uploaded_demo(file, player_name)
    parsed_demo = _parse_demo_for_analysis(saved_path)
    round_features = _extract_features_for_player(parsed_demo, cleaned_player_name)

    csv_rows: list[dict[str, Any]] = []
    for row in round_features:
        csv_row = {column: row.get(column) for column in CSV_COLUMNS}
        csv_row["demo_id"] = demo_id
        csv_row["risk_score"] = calculate_baseline_risk(row)
        csv_rows.append(csv_row)

    FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    resolved_player_name = str(round_features[0].get("player_name", cleaned_player_name))
    csv_path = FEATURE_DIR / f"{demo_id}_{_player_slug(resolved_player_name)}_features.csv"

    dataframe = pd.DataFrame(csv_rows, columns=CSV_COLUMNS)
    dataframe.to_csv(csv_path, index=False)

    response = {
        "player_name": resolved_player_name,
        "rows_written": len(csv_rows),
        "csv_path": str(csv_path),
        "preview": csv_rows[:5],
    }
    return jsonable_encoder(response)
