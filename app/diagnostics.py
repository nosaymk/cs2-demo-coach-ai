from __future__ import annotations

from typing import Any

import pandas as pd

from app.features import _demo_dataframe, _first_existing_column, _int_or_none


def _map_name(demo: Any) -> str | None:
    header = getattr(demo, "header", {}) or {}
    if not isinstance(header, dict):
        return None
    for key in ("map_name", "map", "mapName"):
        value = header.get(key)
        if value:
            return str(value)
    return None


def _clean_value(value: Any) -> Any:
    if value is None:
        return None
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def diagnose_player_positions(demo: Any, sample_size: int = 5) -> dict[str, Any]:
    """
    Verify whether Awpy exposed player position/tick data for a parsed demo.

    Awpy's `demo.ticks` is expected to contain one row per player per in-play
    tick, with player coordinates in X/Y/Z columns when those props are parsed.
    """
    ticks_df = _demo_dataframe(demo, "ticks")
    if ticks_df is None or ticks_df.empty:
        return {
            "map_name": _map_name(demo),
            "number_of_ticks": 0,
            "number_of_player_position_records": 0,
            "sample_player_position_records": [],
            "position_data_available": False,
            "reason": "Awpy did not expose a non-empty demo.ticks dataframe.",
        }

    tick_col = _first_existing_column(ticks_df, ("tick",))
    name_col = _first_existing_column(ticks_df, ("name", "player_name"))
    x_col = _first_existing_column(ticks_df, ("X", "x"))
    y_col = _first_existing_column(ticks_df, ("Y", "y"))
    z_col = _first_existing_column(ticks_df, ("Z", "z"))
    round_col = _first_existing_column(ticks_df, ("round_num", "round", "round_number", "roundNumber"))
    side_col = _first_existing_column(ticks_df, ("side", "player_side", "team_side"))

    if tick_col:
        number_of_ticks = int(ticks_df[tick_col].dropna().map(_int_or_none).dropna().nunique())
    else:
        number_of_ticks = 0

    if not tick_col or not name_col or not x_col or not y_col:
        missing = [
            label
            for label, column in (
                ("tick", tick_col),
                ("player name", name_col),
                ("X coordinate", x_col),
                ("Y coordinate", y_col),
            )
            if column is None
        ]
        return {
            "map_name": _map_name(demo),
            "number_of_ticks": number_of_ticks,
            "number_of_player_position_records": 0,
            "sample_player_position_records": [],
            "position_data_available": False,
            "reason": f"demo.ticks is missing required player position columns: {', '.join(missing)}.",
            "available_tick_columns": list(ticks_df.columns),
        }

    position_rows = ticks_df.dropna(subset=[tick_col, name_col, x_col, y_col]).copy()
    position_rows = position_rows.sort_values(tick_col).head(sample_size)

    sample_columns = [
        column
        for column in (tick_col, round_col, name_col, side_col, x_col, y_col, z_col)
        if column is not None
    ]
    samples: list[dict[str, Any]] = []
    for _, row in position_rows.iterrows():
        sample = {column: _clean_value(row.get(column)) for column in sample_columns}
        samples.append(sample)

    return {
        "map_name": _map_name(demo),
        "number_of_ticks": number_of_ticks,
        "number_of_player_position_records": int(len(ticks_df.dropna(subset=[tick_col, name_col, x_col, y_col]))),
        "sample_player_position_records": samples,
        "position_data_available": bool(samples),
    }
