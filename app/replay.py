"""Replay extraction from real Awpy tick, kill, and utility data."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd

from app.features import (
    ROUND_COLUMNS,
    _add_round_num_from_rounds,
    _clean_scalar,
    _demo_dataframe,
    _first_existing_column,
    _float_or_none,
    _int_or_none,
    _normalize_name,
)
from app.map_config import MapConfigError, get_map_config, world_to_map


DOWNSAMPLE_INTERVAL_TICKS = 32


def _map_name(demo: Any) -> str | None:
    header = getattr(demo, "header", {}) or {}
    if not isinstance(header, dict):
        return None
    for key in ("map_name", "map", "mapName"):
        value = header.get(key)
        if value:
            return str(value)
    return None


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        return value.item()
    return value


def _frame(demo: Any, attr: str, rounds_df: pd.DataFrame | None = None) -> pd.DataFrame | None:
    dataframe = _demo_dataframe(demo, attr)
    if attr in {"ticks", "kills", "grenades"}:
        dataframe = _add_round_num_from_rounds(dataframe, rounds_df, attr)
    return dataframe


def _round_boundaries(rounds_df: pd.DataFrame | None) -> list[dict[str, int | None]]:
    if rounds_df is None or rounds_df.empty:
        return []

    round_col = _first_existing_column(rounds_df, ROUND_COLUMNS)
    start_col = _first_existing_column(rounds_df, ("freeze_end", "start"))
    end_col = _first_existing_column(rounds_df, ("official_end", "end"))
    if not round_col:
        return []

    boundaries: list[dict[str, int | None]] = []
    for _, row in rounds_df.sort_values(round_col).iterrows():
        round_num = _int_or_none(row.get(round_col))
        if round_num is None:
            continue
        boundaries.append(
            {
                "round_number": round_num,
                "tick_start": _int_or_none(row.get(start_col)) if start_col else None,
                "tick_end": _int_or_none(row.get(end_col)) if end_col else None,
            }
        )
    return boundaries


def _coordinate_columns(df: pd.DataFrame | None) -> tuple[str | None, str | None, str | None]:
    return (
        _first_existing_column(df, ("X", "x")),
        _first_existing_column(df, ("Y", "y")),
        _first_existing_column(df, ("Z", "z")),
    )


def _event_coordinate_columns(
    df: pd.DataFrame | None,
    prefixes: tuple[str, ...],
) -> tuple[str | None, str | None, str | None]:
    if df is None:
        return None, None, None

    for prefix in prefixes:
        if prefix:
            for x_col, y_col, z_col in (
                (f"{prefix}_X", f"{prefix}_Y", f"{prefix}_Z"),
                (f"{prefix}_x", f"{prefix}_y", f"{prefix}_z"),
            ):
                if x_col in df.columns and y_col in df.columns:
                    return x_col, y_col, z_col if z_col in df.columns else None
        else:
            x_col, y_col, z_col = _coordinate_columns(df)
            if x_col and y_col:
                return x_col, y_col, z_col

    return None, None, None


def _map_point(
    map_name: str,
    row: pd.Series,
    x_col: str | None,
    y_col: str | None,
    z_col: str | None,
) -> dict[str, float | None] | None:
    if not x_col or not y_col:
        return None

    world_x = _float_or_none(row.get(x_col))
    world_y = _float_or_none(row.get(y_col))
    world_z = _float_or_none(row.get(z_col)) if z_col else None
    if world_x is None or world_y is None:
        return None

    return world_to_map(map_name, world_x, world_y, world_z)


def _death_ticks(kills_df: pd.DataFrame | None) -> dict[tuple[int, str], int]:
    deaths: dict[tuple[int, str], int] = {}
    round_col = _first_existing_column(kills_df, ROUND_COLUMNS)
    victim_col = _first_existing_column(kills_df, ("victim_name", "victim"))
    tick_col = _first_existing_column(kills_df, ("tick", "death_tick"))
    if kills_df is None or not round_col or not victim_col or not tick_col:
        return deaths

    rows = kills_df.dropna(subset=[round_col, victim_col, tick_col]).copy()
    rows["_round"] = rows[round_col].map(_int_or_none)
    rows["_tick"] = rows[tick_col].map(_int_or_none)
    rows = rows.dropna(subset=["_round", "_tick"])
    for _, row in rows.sort_values("_tick").iterrows():
        round_num = _int_or_none(row.get("_round"))
        tick = _int_or_none(row.get("_tick"))
        victim = _normalize_name(row.get(victim_col))
        if round_num is None or tick is None or not victim:
            continue
        deaths.setdefault((round_num, victim), tick)
    return deaths


def _side_lookup(ticks_df: pd.DataFrame | None) -> dict[tuple[int, str], Any]:
    lookup: dict[tuple[int, str], Any] = {}
    round_col = _first_existing_column(ticks_df, ROUND_COLUMNS)
    name_col = _first_existing_column(ticks_df, ("name", "player_name"))
    side_col = _first_existing_column(ticks_df, ("side", "player_side", "team_side"))
    if ticks_df is None or not round_col or not name_col or not side_col:
        return lookup

    rows = ticks_df[[round_col, name_col, side_col]].dropna().drop_duplicates()
    for _, row in rows.iterrows():
        round_num = _int_or_none(row.get(round_col))
        name = _normalize_name(row.get(name_col))
        if round_num is None or not name:
            continue
        lookup.setdefault((round_num, name), _clean_scalar(row.get(side_col)))
    return lookup


def _sample_player_group(group: pd.DataFrame, tick_col: str, downsample_interval_ticks: int) -> pd.DataFrame:
    group = group.sort_values(tick_col).copy()
    first_tick = _int_or_none(group.iloc[0].get(tick_col))
    if first_tick is None:
        return group.head(0)

    sampled = group[(group[tick_col].map(_int_or_none) - first_tick) % downsample_interval_ticks == 0]
    if sampled.empty:
        sampled = group.head(1)

    last_tick = _int_or_none(group.iloc[-1].get(tick_col))
    sampled_last_tick = _int_or_none(sampled.iloc[-1].get(tick_col)) if not sampled.empty else None
    if last_tick is not None and sampled_last_tick != last_tick:
        sampled = pd.concat([sampled, group.tail(1)], ignore_index=False)

    return sampled


def _players_by_round(
    ticks_df: pd.DataFrame | None,
    map_name: str,
    death_tick_lookup: dict[tuple[int, str], int],
    downsample_interval_ticks: int,
) -> dict[int, list[dict[str, Any]]]:
    round_col = _first_existing_column(ticks_df, ROUND_COLUMNS)
    name_col = _first_existing_column(ticks_df, ("name", "player_name"))
    side_col = _first_existing_column(ticks_df, ("side", "player_side", "team_side"))
    tick_col = _first_existing_column(ticks_df, ("tick",))
    x_col, y_col, z_col = _coordinate_columns(ticks_df)
    if ticks_df is None or not round_col or not name_col or not tick_col or not x_col or not y_col:
        return {}

    rows = ticks_df.dropna(subset=[round_col, name_col, tick_col, x_col, y_col]).copy()
    rows["_round"] = rows[round_col].map(_int_or_none)
    rows["_tick"] = rows[tick_col].map(_int_or_none)
    rows = rows.dropna(subset=["_round", "_tick"])

    players: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (round_num, player_name), group in rows.groupby(["_round", name_col], sort=True):
        round_int = int(round_num)
        name = str(player_name)
        side = _clean_scalar(group[side_col].dropna().iloc[0]) if side_col and not group[side_col].dropna().empty else None
        death_tick = death_tick_lookup.get((round_int, _normalize_name(name)))
        sampled = _sample_player_group(group, "_tick", downsample_interval_ticks)

        positions: list[dict[str, Any]] = []
        for _, row in sampled.iterrows():
            tick = _int_or_none(row.get("_tick"))
            if tick is None:
                continue
            mapped = _map_point(map_name, row, x_col, y_col, z_col)
            if mapped is None:
                continue
            positions.append(
                {
                    "tick": tick,
                    "x": round(float(mapped["x"]), 3),
                    "y": round(float(mapped["y"]), 3),
                    "alive": death_tick is None or tick < death_tick,
                }
            )

        if positions:
            players[round_int].append(
                {
                    "name": name,
                    "side": side,
                    "positions": positions,
                }
            )

    return players


def _kills_by_round(kills_df: pd.DataFrame | None, map_name: str) -> dict[int, list[dict[str, Any]]]:
    round_col = _first_existing_column(kills_df, ROUND_COLUMNS)
    tick_col = _first_existing_column(kills_df, ("tick", "death_tick"))
    attacker_col = _first_existing_column(kills_df, ("attacker_name", "attacker"))
    victim_col = _first_existing_column(kills_df, ("victim_name", "victim"))
    attacker_side_col = _first_existing_column(kills_df, ("attacker_side", "attacker_team_side"))
    victim_side_col = _first_existing_column(kills_df, ("victim_side", "victim_team_side"))
    weapon_col = _first_existing_column(kills_df, ("weapon", "weapon_name", "gun"))
    x_col, y_col, z_col = _event_coordinate_columns(kills_df, ("victim", "user", ""))
    if kills_df is None or not round_col or not tick_col:
        return {}

    kills: dict[int, list[dict[str, Any]]] = defaultdict(list)
    rows = kills_df.dropna(subset=[round_col, tick_col]).copy()
    rows["_round"] = rows[round_col].map(_int_or_none)
    rows["_tick"] = rows[tick_col].map(_int_or_none)
    rows = rows.dropna(subset=["_round", "_tick"]).sort_values("_tick")
    for _, row in rows.iterrows():
        round_num = _int_or_none(row.get("_round"))
        tick = _int_or_none(row.get("_tick"))
        if round_num is None or tick is None:
            continue
        mapped = _map_point(map_name, row, x_col, y_col, z_col)
        event = {
            "tick": tick,
            "attacker": _clean_scalar(row.get(attacker_col)) if attacker_col else None,
            "victim": _clean_scalar(row.get(victim_col)) if victim_col else None,
            "attacker_side": _clean_scalar(row.get(attacker_side_col)) if attacker_side_col else None,
            "victim_side": _clean_scalar(row.get(victim_side_col)) if victim_side_col else None,
            "weapon": _clean_scalar(row.get(weapon_col)) if weapon_col else None,
        }
        if mapped is not None:
            event["x"] = round(float(mapped["x"]), 3)
            event["y"] = round(float(mapped["y"]), 3)
        kills[round_num].append(event)
    return kills


def _utility_by_round(
    grenades_df: pd.DataFrame | None,
    map_name: str,
    side_lookup: dict[tuple[int, str], Any],
) -> dict[int, list[dict[str, Any]]]:
    round_col = _first_existing_column(grenades_df, ROUND_COLUMNS)
    tick_col = _first_existing_column(grenades_df, ("tick", "throw_tick", "start_tick"))
    thrower_col = _first_existing_column(grenades_df, ("thrower", "thrower_name", "player_name", "name"))
    grenade_col = _first_existing_column(grenades_df, ("grenade_type", "weapon", "projectile_type"))
    entity_col = _first_existing_column(grenades_df, ("entity_id", "grenade_entity_id"))
    x_col, y_col, z_col = _coordinate_columns(grenades_df)
    if grenades_df is None or not round_col or not tick_col or not thrower_col or not grenade_col:
        return {}

    rows = grenades_df.dropna(subset=[round_col, tick_col, thrower_col, grenade_col]).copy()
    if entity_col:
        rows = rows.drop_duplicates(subset=[round_col, entity_col, grenade_col])
    else:
        rows = rows.drop_duplicates(subset=[round_col, tick_col, thrower_col, grenade_col])

    rows["_round"] = rows[round_col].map(_int_or_none)
    rows["_tick"] = rows[tick_col].map(_int_or_none)
    rows = rows.dropna(subset=["_round", "_tick"]).sort_values("_tick")

    utility: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for _, row in rows.iterrows():
        round_num = _int_or_none(row.get("_round"))
        tick = _int_or_none(row.get("_tick"))
        thrower = _clean_scalar(row.get(thrower_col))
        if round_num is None or tick is None:
            continue
        mapped = _map_point(map_name, row, x_col, y_col, z_col)
        event = {
            "tick": tick,
            "thrower": thrower,
            "side": side_lookup.get((round_num, _normalize_name(thrower))),
            "grenade_type": _clean_scalar(row.get(grenade_col)),
            "entity_id": _json_value(row.get(entity_col)) if entity_col else None,
        }
        if mapped is not None:
            event["x"] = round(float(mapped["x"]), 3)
            event["y"] = round(float(mapped["y"]), 3)
        utility[round_num].append(event)
    return utility


def extract_replay_data(
    demo: Any,
    selected_player: str | None = None,
    downsample_interval_ticks: int = DOWNSAMPLE_INTERVAL_TICKS,
) -> dict[str, Any]:
    """
    Extract real CS2 replay data from Awpy tick/event data.

    Player locations are downsampled from `demo.ticks`; no mock players or
    coordinates are generated.
    """
    map_name = _map_name(demo)
    if not map_name:
        return {
            "replay_available": False,
            "reason": "Awpy did not expose a map name in demo.header.",
            "map_name": None,
            "map_config": None,
            "selected_player": selected_player,
            "downsample_interval_ticks": downsample_interval_ticks,
            "rounds": [],
        }

    map_config = get_map_config(map_name)
    if map_config is None:
        return {
            "replay_available": False,
            "reason": f"No map config exists for map '{map_name}'. Add it to app/map_config.py.",
            "map_name": map_name,
            "map_config": None,
            "selected_player": selected_player,
            "downsample_interval_ticks": downsample_interval_ticks,
            "rounds": [],
        }

    rounds_df = _frame(demo, "rounds")
    ticks_df = _frame(demo, "ticks", rounds_df)
    kills_df = _frame(demo, "kills", rounds_df)
    grenades_df = _frame(demo, "grenades", rounds_df)

    if ticks_df is None or ticks_df.empty:
        return {
            "replay_available": False,
            "reason": "Awpy did not expose non-empty demo.ticks data.",
            "map_name": map_name,
            "map_config": map_config,
            "selected_player": selected_player,
            "downsample_interval_ticks": downsample_interval_ticks,
            "rounds": [],
        }

    try:
        deaths = _death_ticks(kills_df)
        sides = _side_lookup(ticks_df)
        players = _players_by_round(ticks_df, map_name, deaths, downsample_interval_ticks)
        kills = _kills_by_round(kills_df, map_name)
        utility = _utility_by_round(grenades_df, map_name, sides)
    except MapConfigError as exc:
        return {
            "replay_available": False,
            "reason": str(exc),
            "map_name": map_name,
            "map_config": map_config,
            "selected_player": selected_player,
            "downsample_interval_ticks": downsample_interval_ticks,
            "rounds": [],
        }

    rounds: list[dict[str, Any]] = []
    for boundary in _round_boundaries(rounds_df):
        round_num = int(boundary["round_number"])
        rounds.append(
            {
                "round_number": round_num,
                "map_name": map_name,
                "tick_start": boundary["tick_start"],
                "tick_end": boundary["tick_end"],
                "players": players.get(round_num, []),
                "kills": kills.get(round_num, []),
                "utility": utility.get(round_num, []),
            }
        )

    if not rounds:
        return {
            "replay_available": False,
            "reason": "Could not identify round boundaries from Awpy data.",
            "map_name": map_name,
            "map_config": map_config,
            "selected_player": selected_player,
            "downsample_interval_ticks": downsample_interval_ticks,
            "rounds": [],
        }

    return {
        "replay_available": True,
        "reason": None,
        "map_name": map_name,
        "map_config": map_config,
        "selected_player": selected_player,
        "downsample_interval_ticks": downsample_interval_ticks,
        "rounds": rounds,
    }
