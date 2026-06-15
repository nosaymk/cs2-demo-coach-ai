"""Pydantic response schemas for public FastAPI endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "cs-demo-coach-ai"


class RoundReport(BaseModel):
    round: int | None
    risk_score: float
    bad_round_prediction: int | None = None
    bad_round_probability: float | None = None
    detected_issues: list[str]
    raw_features: dict[str, Any]


class AnalysisReport(BaseModel):
    player: str
    rounds_analyzed: int = Field(ge=0)
    overall_risk_score: float | None
    model_status: str
    round_reports: list[RoundReport]
    missing_features_summary: dict[str, int]


class FeatureExportResponse(BaseModel):
    player_name: str
    rows_written: int = Field(ge=0)
    csv_path: str
    preview: list[dict[str, Any]]


class PositionDiagnosticResponse(BaseModel):
    map_name: str | None
    number_of_ticks: int = Field(ge=0)
    number_of_player_position_records: int = Field(ge=0)
    sample_player_position_records: list[dict[str, Any]]
    position_data_available: bool
    reason: str | None = None
    available_tick_columns: list[str] | None = None


class ReplayDataResponse(BaseModel):
    replay_available: bool
    reason: str | None = None
    map_name: str | None
    map_config: dict[str, Any] | None
    selected_player: str | None = None
    downsample_interval_ticks: int = Field(ge=1)
    rounds: list[dict[str, Any]]


class ModelInfoResponse(BaseModel):
    model_status: str
    model_path: str
    model_exists: bool
    model_type: str | None
    feature_columns: list[str] | None = None
    last_modified: str | None = None
    load_error: str | None = None


class ErrorResponse(BaseModel):
    detail: str
