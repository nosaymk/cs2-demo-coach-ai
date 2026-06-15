"""Feature extraction helpers for real Awpy parser outputs.

The module is defensive because Awpy dataframe columns can vary by parser
version and demo type. Missing values are surfaced explicitly instead of
inventing synthetic Counter-Strike events.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

import pandas as pd


class FeatureExtractionError(RuntimeError):
    """Raised when real parsed demo data is present but cannot be analyzed."""


class PlayerNotFoundError(FeatureExtractionError):
    """Raised when the requested player is not visible in parsed demo data."""


ROUND_COLUMNS = ("round_num", "round", "round_number", "roundNumber")
PLAYER_NAME_COLUMNS = (
    "name",
    "player_name",
    "attacker_name",
    "victim_name",
    "thrower",
    "thrower_name",
)


def _to_pandas(value: Any) -> pd.DataFrame | None:
    if value is None:
        return None
    if isinstance(value, pd.DataFrame):
        return value.copy()
    if hasattr(value, "to_pandas"):
        return value.to_pandas()
    if hasattr(value, "collect") and hasattr(value.collect(), "to_pandas"):
        return value.collect().to_pandas()
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        try:
            return pd.DataFrame(value)
        except ValueError:
            return pd.DataFrame([value])
    return None


def _demo_dataframe(demo: Any, attr: str) -> pd.DataFrame | None:
    return _to_pandas(getattr(demo, attr, None))


def _first_existing_column(df: pd.DataFrame | None, candidates: Iterable[str]) -> str | None:
    if df is None:
        return None
    for column in candidates:
        if column in df.columns:
            return column
    return None


def _normalize_name(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().casefold()


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def _int_or_none(value: Any) -> int | None:
    value = _json_value(value)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    value = _json_value(value)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_scalar(value: Any) -> Any:
    value = _json_value(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def _available_columns(demo_frames: dict[str, pd.DataFrame | None]) -> dict[str, list[str]]:
    return {
        name: list(df.columns)
        for name, df in demo_frames.items()
        if df is not None and not df.empty
    }


def _collect_player_names(frames: Iterable[pd.DataFrame | None]) -> set[str]:
    players: set[str] = set()
    for df in frames:
        if df is None or df.empty:
            continue
        for column in PLAYER_NAME_COLUMNS:
            if column in df.columns:
                for value in df[column].dropna().unique().tolist():
                    name = str(value).strip()
                    if name:
                        players.add(name)
    return players


def _resolve_player_name(player_name: str, frames: Iterable[pd.DataFrame | None]) -> str:
    requested = player_name.strip()
    if not requested:
        raise FeatureExtractionError("player_name cannot be empty.")

    players = _collect_player_names(frames)
    for known in players:
        if known == requested:
            return known
    for known in players:
        if _normalize_name(known) == _normalize_name(requested):
            return known

    available = sorted(players)[:50]
    raise PlayerNotFoundError(
        f"Player '{requested}' was not found in parsed demo data. "
        f"Available players include: {available}"
    )


def _add_round_num_from_rounds(
    df: pd.DataFrame | None,
    rounds_df: pd.DataFrame | None,
    source_name: str,
) -> pd.DataFrame | None:
    if df is None or df.empty:
        return df
    if _first_existing_column(df, ROUND_COLUMNS):
        return df

    tick_col = _first_existing_column(df, ("tick", "start_tick"))
    round_col = _first_existing_column(rounds_df, ROUND_COLUMNS)
    start_col = _first_existing_column(rounds_df, ("start", "freeze_end"))
    end_col = _first_existing_column(rounds_df, ("end", "official_end"))
    if not tick_col or not round_col or not start_col or not end_col:
        return df

    intervals = []
    for _, row in rounds_df.iterrows():
        start = _int_or_none(row.get(start_col))
        end = _int_or_none(row.get(end_col))
        round_num = _int_or_none(row.get(round_col))
        if start is None or end is None or round_num is None:
            continue
        intervals.append((start, end, round_num))

    if not intervals:
        return df

    def locate_round(tick: Any) -> int | None:
        tick_value = _int_or_none(tick)
        if tick_value is None:
            return None
        for start, end, round_num in intervals:
            if start <= tick_value <= end:
                return round_num
        return None

    result = df.copy()
    result["round_num"] = result[tick_col].map(locate_round)
    result.attrs["round_source_note"] = (
        f"{source_name}.round_num inferred from {source_name}.{tick_col} "
        "using rounds start/end ticks."
    )
    return result


def _round_numbers(
    rounds_df: pd.DataFrame | None,
    ticks_df: pd.DataFrame | None,
    event_frames: Iterable[pd.DataFrame | None],
    player_name: str,
) -> list[int]:
    tick_round_col = _first_existing_column(ticks_df, ROUND_COLUMNS)
    tick_name_col = _first_existing_column(ticks_df, ("name", "player_name"))
    if ticks_df is not None and tick_round_col:
        source = ticks_df
        if tick_name_col:
            source = source[source[tick_name_col].map(_normalize_name) == _normalize_name(player_name)]
        rounds = sorted(
            {
                _int_or_none(value)
                for value in source[tick_round_col].dropna().tolist()
                if _int_or_none(value) is not None
            }
        )
        if rounds:
            return rounds

    round_col = _first_existing_column(rounds_df, ROUND_COLUMNS)
    if rounds_df is not None and round_col:
        values = rounds_df[round_col].dropna().tolist()
        rounds = sorted({_int_or_none(value) for value in values if _int_or_none(value) is not None})
        if rounds:
            return rounds

    found: set[int] = set()
    for df in event_frames:
        round_col = _first_existing_column(df, ROUND_COLUMNS)
        if df is None or not round_col:
            continue
        for value in df[round_col].dropna().tolist():
            round_num = _int_or_none(value)
            if round_num is not None:
                found.add(round_num)
    return sorted(found)

def _sum_damage(df: pd.DataFrame | None, player_name: str, round_num: int) -> int | None:
    # Source: Awpy demo.damages. It records each damage event, including
    # attacker_name, victim_name and dmg_health_real when the parser exposes it.
    attacker_col = _first_existing_column(df, ("attacker_name", "attacker", "player_name", "name"))
    round_col = _first_existing_column(df, ROUND_COLUMNS)
    damage_col = _first_existing_column(df, ("dmg_health_real", "dmg_health", "health_damage", "damage"))
    if df is None or not attacker_col or not round_col or not damage_col:
        return None

    player_rows = df[
        (df[attacker_col].map(_normalize_name) == _normalize_name(player_name))
        & (df[round_col].map(_int_or_none) == round_num)
    ]
    return int(player_rows[damage_col].fillna(0).sum())


def _utility_counts(
    grenades_df: pd.DataFrame | None,
    shots_df: pd.DataFrame | None,
    player_name: str,
    round_num: int,
) -> tuple[dict[str, int | None], list[str]]:
    missing: list[str] = []
    counts: dict[str, int | None] = {
        "flashes_thrown": None,
        "smokes_thrown": None,
        "molotovs_incendiaries_thrown": None,
        "he_grenades_thrown": None,
    }

    # Primary source: Awpy demo.grenades. It contains thrower, grenade_type,
    # entity_id, tick and round_num. Rows can repeat across grenade trajectory
    # ticks, so throws are counted by unique entity_id where available.
    thrower_col = _first_existing_column(grenades_df, ("thrower", "thrower_name", "player_name", "name"))
    grenade_col = _first_existing_column(grenades_df, ("grenade_type", "weapon", "projectile_type"))
    round_col = _first_existing_column(grenades_df, ROUND_COLUMNS)
    if grenades_df is not None and thrower_col and grenade_col and round_col:
        rows = grenades_df[
            (grenades_df[thrower_col].map(_normalize_name) == _normalize_name(player_name))
            & (grenades_df[round_col].map(_int_or_none) == round_num)
        ].copy()
        entity_col = _first_existing_column(rows, ("entity_id", "grenade_entity_id"))
        tick_col = _first_existing_column(rows, ("tick", "throw_tick", "start_tick"))
        if entity_col:
            rows = rows.drop_duplicates(subset=[entity_col, grenade_col])
        elif tick_col:
            rows = rows.drop_duplicates(subset=[tick_col, grenade_col])

        values = rows[grenade_col].dropna().map(lambda value: str(value).casefold()).tolist()
    else:
        values = []

    if not values:
        # Fallback source: Awpy demo.shots. Grenade weapon_fire rows are real
        # events, but this is only used when demo.grenades is unavailable.
        player_col = _first_existing_column(shots_df, ("player_name", "name"))
        weapon_col = _first_existing_column(shots_df, ("weapon", "weapon_name"))
        shot_round_col = _first_existing_column(shots_df, ROUND_COLUMNS)
        if shots_df is not None and player_col and weapon_col and shot_round_col:
            rows = shots_df[
                (shots_df[player_col].map(_normalize_name) == _normalize_name(player_name))
                & (shots_df[shot_round_col].map(_int_or_none) == round_num)
            ]
            values = rows[weapon_col].dropna().map(lambda value: str(value).casefold()).tolist()

    if not values and not (
        grenades_df is not None and thrower_col and grenade_col and round_col
    ) and not (
        shots_df is not None
        and _first_existing_column(shots_df, ("player_name", "name"))
        and _first_existing_column(shots_df, ("weapon", "weapon_name"))
        and _first_existing_column(shots_df, ROUND_COLUMNS)
    ):
        missing.extend(counts.keys())
        return counts, missing

    counts["flashes_thrown"] = sum("flash" in value for value in values)
    counts["smokes_thrown"] = sum("smoke" in value for value in values)
    counts["molotovs_incendiaries_thrown"] = sum(
        ("molotov" in value) or ("incendiary" in value) or ("inferno" in value)
        for value in values
    )
    counts["he_grenades_thrown"] = sum(
        ("hegrenade" in value)
        or ("he_grenade" in value)
        or value.endswith("_he")
        or value == "he"
        or ("frag" in value)
        for value in values
    )
    return counts, missing


def _first_death_info(
    kills_df: pd.DataFrame | None,
    player_name: str,
    round_num: int,
    rounds_df: pd.DataFrame | None,
    demo: Any,
) -> tuple[int | None, bool | None, float | None]:
    # Source: Awpy demo.kills. Victim rows are deaths; the earliest death tick
    # in a round is used to derive died_first.
    victim_col = _first_existing_column(kills_df, ("victim_name", "victim"))
    round_col = _first_existing_column(kills_df, ROUND_COLUMNS)
    tick_col = _first_existing_column(kills_df, ("tick", "death_tick"))
    if kills_df is None or not victim_col or not round_col:
        return None, None, None

    deaths_in_round = kills_df[kills_df[round_col].map(_int_or_none) == round_num].copy()
    player_deaths = deaths_in_round[
        deaths_in_round[victim_col].map(_normalize_name) == _normalize_name(player_name)
    ]
    if player_deaths.empty:
        return None, False if not deaths_in_round.empty else None, None

    if not tick_col:
        return None, None, None

    death_tick = _int_or_none(player_deaths[tick_col].min())
    first_tick = _int_or_none(deaths_in_round[tick_col].min())
    died_first = death_tick is not None and first_tick is not None and death_tick == first_tick
    return death_tick, died_first, _death_time_seconds(death_tick, round_num, rounds_df, demo)


def _death_time_seconds(
    death_tick: int | None,
    round_num: int,
    rounds_df: pd.DataFrame | None,
    demo: Any,
) -> float | None:
    if death_tick is None or rounds_df is None or rounds_df.empty:
        return None

    header = getattr(demo, "header", {}) or {}
    tick_rate = None
    if isinstance(header, dict):
        for key in ("tick_rate", "tickrate", "ticks_per_second"):
            tick_rate = _float_or_none(header.get(key))
            if tick_rate:
                break
    if not tick_rate:
        return None

    round_col = _first_existing_column(rounds_df, ROUND_COLUMNS)
    start_col = _first_existing_column(rounds_df, ("freeze_end", "start"))
    if not round_col or not start_col:
        return None

    row = rounds_df[rounds_df[round_col].map(_int_or_none) == round_num]
    if row.empty:
        return None
    start_tick = _int_or_none(row.iloc[0].get(start_col))
    if start_tick is None:
        return None

    return round((death_tick - start_tick) / tick_rate, 3)


def _round_side_team(
    ticks_df: pd.DataFrame | None,
    event_frames: Iterable[pd.DataFrame | None],
    player_name: str,
    round_num: int,
) -> tuple[Any, Any]:
    # Preferred source: Awpy demo.ticks. If the user parsed side/team props,
    # ticks can include per-player side or team columns for each round.
    def side_candidates_for(name_col: str) -> tuple[str, ...]:
        if name_col.startswith("attacker"):
            return ("attacker_side", "attacker_team_side", "side", "player_side", "team_side")
        if name_col.startswith("victim"):
            return ("victim_side", "victim_team_side", "side", "player_side", "team_side")
        return ("side", "player_side", "team_side", "attacker_side", "victim_side")

    def team_candidates_for(name_col: str) -> tuple[str, ...]:
        if name_col.startswith("attacker"):
            return (
                "attacker_team_name",
                "attacker_team",
                "attacker_clan",
                "team_name",
                "team",
                "player_team_name",
            )
        if name_col.startswith("victim"):
            return (
                "victim_team_name",
                "victim_team",
                "victim_clan",
                "team_name",
                "team",
                "player_team_name",
            )
        return (
            "team",
            "team_name",
            "player_team_name",
            "clan",
            "player_clan",
            "attacker_team_name",
            "victim_team_name",
        )

    for df, name_candidates in (
        (ticks_df, ("name", "player_name")),
        *[(frame, ("attacker_name", "victim_name", "player_name", "name")) for frame in event_frames],
    ):
        if df is None or df.empty:
            continue
        round_col = _first_existing_column(df, ROUND_COLUMNS)
        if not round_col:
            continue

        name_col = None
        for candidate in name_candidates:
            if candidate in df.columns:
                name_col = candidate
                break
        if not name_col:
            continue

        rows = df[
            (df[round_col].map(_int_or_none) == round_num)
            & (df[name_col].map(_normalize_name) == _normalize_name(player_name))
        ]
        if rows.empty:
            continue

        side_col = _first_existing_column(rows, side_candidates_for(name_col))
        team_col = _first_existing_column(rows, team_candidates_for(name_col))
        side = _clean_scalar(rows[side_col].dropna().iloc[0]) if side_col and not rows[side_col].dropna().empty else None
        team = _clean_scalar(rows[team_col].dropna().iloc[0]) if team_col and not rows[team_col].dropna().empty else None
        if side is not None or team is not None:
            return side, team

    return None, None


def _count_rows(
    df: pd.DataFrame | None,
    player_column_candidates: Iterable[str],
    player_name: str,
    round_num: int,
) -> int | None:
    player_col = _first_existing_column(df, player_column_candidates)
    round_col = _first_existing_column(df, ROUND_COLUMNS)
    if df is None or not player_col or not round_col:
        return None
    rows = df[
        (df[player_col].map(_normalize_name) == _normalize_name(player_name))
        & (df[round_col].map(_int_or_none) == round_num)
    ]
    return int(len(rows))


def _normalize_side(value: Any) -> str:
    side = _normalize_name(value)
    if side in {"ct", "counterterrorist", "counter-terrorist", "counter_terrorist"}:
        return "ct"
    if side in {"t", "terrorist"}:
        return "t"
    return side


def _round_rows(df: pd.DataFrame | None, round_num: int) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    round_col = _first_existing_column(df, ROUND_COLUMNS)
    if not round_col:
        return pd.DataFrame()

    return df[df[round_col].map(_int_or_none) == round_num].copy()


def _first_kill_details(
    kills_df: pd.DataFrame | None,
    player_name: str,
    round_num: int,
) -> tuple[bool | None, int | None, int | None]:
    attacker_col = _first_existing_column(kills_df, ("attacker_name", "attacker", "player_name"))
    tick_col = _first_existing_column(kills_df, ("tick", "death_tick"))
    if kills_df is None or not attacker_col or not tick_col or not _first_existing_column(kills_df, ROUND_COLUMNS):
        return None, None, None

    rows = _round_rows(kills_df, round_num)
    if rows.empty:
        return False, None, None

    rows = rows.assign(_tick=rows[tick_col].map(_int_or_none)).dropna(subset=["_tick"]).sort_values("_tick")
    if rows.empty:
        return None, None, None

    first_row = rows.iloc[0]
    player_rows = rows[rows[attacker_col].map(_normalize_name) == _normalize_name(player_name)]
    first_player_kill_tick = _int_or_none(player_rows["_tick"].min()) if not player_rows.empty else None
    opening_kill = _normalize_name(first_row.get(attacker_col)) == _normalize_name(player_name)
    return opening_kill, _int_or_none(first_row.get("_tick")), first_player_kill_tick


def _kills_before_death(
    kills_df: pd.DataFrame | None,
    player_name: str,
    round_num: int,
    death_tick: int | None,
) -> int | None:
    attacker_col = _first_existing_column(kills_df, ("attacker_name", "attacker", "player_name"))
    tick_col = _first_existing_column(kills_df, ("tick", "death_tick"))
    if kills_df is None or not attacker_col or not tick_col or not _first_existing_column(kills_df, ROUND_COLUMNS):
        return None

    rows = _round_rows(kills_df, round_num)
    player_kills = rows[rows[attacker_col].map(_normalize_name) == _normalize_name(player_name)].copy()
    if death_tick is not None:
        player_kills = player_kills[player_kills[tick_col].map(_int_or_none) < death_tick]
    return int(len(player_kills))


def _damage_before_death(
    damages_df: pd.DataFrame | None,
    player_name: str,
    round_num: int,
    death_tick: int | None,
) -> int | None:
    attacker_col = _first_existing_column(damages_df, ("attacker_name", "attacker", "player_name", "name"))
    tick_col = _first_existing_column(damages_df, ("tick", "damage_tick"))
    damage_col = _first_existing_column(damages_df, ("dmg_health_real", "dmg_health", "health_damage", "damage"))
    if (
        damages_df is None
        or not attacker_col
        or not tick_col
        or not damage_col
        or not _first_existing_column(damages_df, ROUND_COLUMNS)
    ):
        return None

    rows = _round_rows(damages_df, round_num)
    player_damage = rows[rows[attacker_col].map(_normalize_name) == _normalize_name(player_name)].copy()
    if death_tick is not None:
        player_damage = player_damage[player_damage[tick_col].map(_int_or_none) < death_tick]
    return int(player_damage[damage_col].fillna(0).sum())


def _utility_used_before_death(
    grenades_df: pd.DataFrame | None,
    shots_df: pd.DataFrame | None,
    player_name: str,
    round_num: int,
    death_tick: int | None,
) -> int | None:
    thrower_col = _first_existing_column(grenades_df, ("thrower", "thrower_name", "player_name", "name"))
    grenade_col = _first_existing_column(grenades_df, ("grenade_type", "weapon", "projectile_type"))
    tick_col = _first_existing_column(grenades_df, ("tick", "throw_tick", "start_tick"))
    if (
        grenades_df is not None
        and thrower_col
        and grenade_col
        and tick_col
        and _first_existing_column(grenades_df, ROUND_COLUMNS)
    ):
        rows = _round_rows(grenades_df, round_num)
        rows = rows[rows[thrower_col].map(_normalize_name) == _normalize_name(player_name)].copy()
        if death_tick is not None:
            rows = rows[rows[tick_col].map(_int_or_none) < death_tick]

        entity_col = _first_existing_column(rows, ("entity_id", "grenade_entity_id"))
        if entity_col:
            rows = rows.drop_duplicates(subset=[entity_col, grenade_col])
        else:
            rows = rows.drop_duplicates(subset=[tick_col, grenade_col])
        return int(len(rows))

    player_col = _first_existing_column(shots_df, ("player_name", "name"))
    weapon_col = _first_existing_column(shots_df, ("weapon", "weapon_name"))
    shot_tick_col = _first_existing_column(shots_df, ("tick", "shot_tick"))
    if (
        shots_df is None
        or not player_col
        or not weapon_col
        or not shot_tick_col
        or not _first_existing_column(shots_df, ROUND_COLUMNS)
    ):
        return None

    rows = _round_rows(shots_df, round_num)
    rows = rows[rows[player_col].map(_normalize_name) == _normalize_name(player_name)].copy()
    if death_tick is not None:
        rows = rows[rows[shot_tick_col].map(_int_or_none) < death_tick]

    utility_terms = ("flash", "smoke", "molotov", "incendiary", "hegrenade", "he_grenade")
    weapons = rows[weapon_col].dropna().map(lambda value: str(value).casefold())
    return int(weapons.map(lambda value: any(term in value for term in utility_terms)).sum())


def _round_win(rounds_df: pd.DataFrame | None, player_side: Any, round_num: int) -> bool | None:
    if rounds_df is None or rounds_df.empty:
        return None

    winner_col = _first_existing_column(rounds_df, ("winner", "winning_side", "round_winner"))
    round_col = _first_existing_column(rounds_df, ROUND_COLUMNS)
    if not winner_col or not round_col:
        return None

    player_side_normalized = _normalize_side(player_side)
    if not player_side_normalized:
        return None

    rows = rounds_df[rounds_df[round_col].map(_int_or_none) == round_num]
    if rows.empty:
        return None

    winner = _normalize_side(rows.iloc[0].get(winner_col))
    if not winner:
        return None
    return winner == player_side_normalized


def _round_roster_from_ticks(
    ticks_df: pd.DataFrame | None,
    round_num: int,
) -> dict[str, set[str]] | None:
    name_col = _first_existing_column(ticks_df, ("name", "player_name"))
    side_col = _first_existing_column(ticks_df, ("side", "player_side", "team_side"))
    if ticks_df is None or not name_col or not side_col or not _first_existing_column(ticks_df, ROUND_COLUMNS):
        return None

    rows = _round_rows(ticks_df, round_num)
    if rows.empty:
        return None

    roster = {"ct": set(), "t": set()}
    for _, row in rows[[name_col, side_col]].dropna().drop_duplicates().iterrows():
        name = str(row.get(name_col)).strip()
        side = _normalize_side(row.get(side_col))
        if name and side in roster:
            roster[side].add(name)

    if not roster["ct"] or not roster["t"]:
        return None
    return roster


def _alive_context_features(
    ticks_df: pd.DataFrame | None,
    kills_df: pd.DataFrame | None,
    player_name: str,
    player_side: Any,
    round_num: int,
    death_tick: int | None,
) -> tuple[dict[str, Any], list[str]]:
    features = {
        "clutch_situation": None,
        "team_alive_when_player_died": None,
        "enemies_alive_when_player_died": None,
    }
    missing: list[str] = []

    roster = _round_roster_from_ticks(ticks_df, round_num)
    player_side_normalized = _normalize_side(player_side)
    if roster is None or player_side_normalized not in roster:
        return features, ["clutch_situation", "team_alive_when_player_died", "enemies_alive_when_player_died"]

    resolved_player = None
    for roster_name in roster[player_side_normalized]:
        if _normalize_name(roster_name) == _normalize_name(player_name):
            resolved_player = roster_name
            break
    if resolved_player is None:
        return features, ["clutch_situation", "team_alive_when_player_died", "enemies_alive_when_player_died"]

    enemy_side = "ct" if player_side_normalized == "t" else "t"
    alive = {"ct": set(roster["ct"]), "t": set(roster["t"])}

    victim_col = _first_existing_column(kills_df, ("victim_name", "victim"))
    victim_side_col = _first_existing_column(kills_df, ("victim_side", "side", "player_side"))
    tick_col = _first_existing_column(kills_df, ("tick", "death_tick"))
    if kills_df is None or not victim_col or not tick_col or not _first_existing_column(kills_df, ROUND_COLUMNS):
        return features, ["clutch_situation", "team_alive_when_player_died", "enemies_alive_when_player_died"]

    kills = _round_rows(kills_df, round_num)
    kills = kills.assign(_tick=kills[tick_col].map(_int_or_none)).dropna(subset=["_tick"]).sort_values("_tick")

    def player_is_in_clutch() -> bool:
        return (
            resolved_player in alive[player_side_normalized]
            and alive[player_side_normalized] == {resolved_player}
            and len(alive[enemy_side]) > 0
        )

    clutch_seen = player_is_in_clutch()
    death_seen = False
    for _, kill in kills.iterrows():
        tick = _int_or_none(kill.get("_tick"))
        victim_name = str(kill.get(victim_col, "")).strip()
        victim_side = _normalize_side(kill.get(victim_side_col)) if victim_side_col else ""
        if victim_side not in alive:
            for side_name, names in alive.items():
                if any(_normalize_name(name) == _normalize_name(victim_name) for name in names):
                    victim_side = side_name
                    break

        if victim_side in alive:
            matching_names = [name for name in alive[victim_side] if _normalize_name(name) == _normalize_name(victim_name)]
            for name in matching_names:
                alive[victim_side].discard(name)

        if _normalize_name(victim_name) == _normalize_name(resolved_player):
            features["team_alive_when_player_died"] = len(alive[player_side_normalized])
            features["enemies_alive_when_player_died"] = len(alive[enemy_side])
            death_seen = True
            break

        if death_tick is None or tick is None or tick < death_tick:
            clutch_seen = clutch_seen or player_is_in_clutch()

    features["clutch_situation"] = clutch_seen
    if death_tick is not None and not death_seen:
        missing.extend(["team_alive_when_player_died", "enemies_alive_when_player_died"])

    return features, missing


def extract_player_round_features(demo: Any, player_name: str) -> list[dict[str, Any]]:
    """
    Extract real per-round player features from Awpy parser output.

    No mock rows are created. Feature values are derived from parsed Awpy
    dataframes when their data source and required columns exist; otherwise the
    value is set to None and the field is listed in missing_features.
    """
    frames = {
        "rounds": _demo_dataframe(demo, "rounds"),
        "kills": _demo_dataframe(demo, "kills"),
        "damages": _demo_dataframe(demo, "damages"),
        "grenades": _demo_dataframe(demo, "grenades"),
        "shots": _demo_dataframe(demo, "shots"),
        "ticks": _demo_dataframe(demo, "ticks"),
    }

    for name in ("kills", "damages", "grenades", "shots", "ticks"):
        frames[name] = _add_round_num_from_rounds(frames[name], frames["rounds"], name)

    resolved_player = _resolve_player_name(player_name, frames.values())
    rounds = _round_numbers(
        frames["rounds"],
        frames["ticks"],
        (frames["kills"], frames["damages"], frames["grenades"], frames["shots"]),
        resolved_player,
    )
    if not rounds:
        raise FeatureExtractionError(
            "Could not identify any rounds from parsed demo data. "
            f"Available columns: {_available_columns(frames)}"
        )

    results: list[dict[str, Any]] = []
    for round_num in rounds:
        missing_features: list[str] = []

        # Source: Awpy demo.kills, attacker_name/victim_name grouped by round_num.
        kills = _count_rows(frames["kills"], ("attacker_name", "attacker", "player_name"), resolved_player, round_num)
        deaths = _count_rows(frames["kills"], ("victim_name", "victim"), resolved_player, round_num)

        if kills is None:
            missing_features.append("kills")
        if deaths is None:
            missing_features.append("deaths")

        damage_dealt = _sum_damage(frames["damages"], resolved_player, round_num)
        if damage_dealt is None:
            missing_features.append("damage_dealt")

        utility_counts, utility_missing = _utility_counts(
            frames["grenades"],
            frames["shots"],
            resolved_player,
            round_num,
        )
        missing_features.extend(utility_missing)

        death_tick, died_first, death_time = _first_death_info(
            frames["kills"],
            resolved_player,
            round_num,
            frames["rounds"],
            demo,
        )

        if deaths is None:
            survived_round = None
            missing_features.append("survived_round")
        else:
            survived_round = deaths == 0

        if died_first is None:
            missing_features.append("died_first")
        if death_tick is None and deaths:
            missing_features.append("death_tick")
        if death_time is None and deaths:
            missing_features.append("death_time")

        side, team = _round_side_team(
            frames["ticks"],
            (frames["kills"], frames["damages"], frames["shots"]),
            resolved_player,
            round_num,
        )
        if side is None:
            missing_features.append("side")
        if team is None:
            missing_features.append("team")

        utility_values = [value for value in utility_counts.values() if value is not None]
        utility_count = sum(utility_values) if utility_values else None
        if utility_count is None:
            missing_features.append("utility_count")

        opening_kill, _first_kill_tick, first_player_kill_tick = _first_kill_details(
            frames["kills"],
            resolved_player,
            round_num,
        )
        if opening_kill is None:
            missing_features.append("opening_kill")

        opening_death = died_first
        if opening_death is None:
            missing_features.append("opening_death")

        kills_before_death = _kills_before_death(
            frames["kills"],
            resolved_player,
            round_num,
            death_tick,
        )
        if kills_before_death is None:
            missing_features.append("kills_before_death")

        damage_before_death = _damage_before_death(
            frames["damages"],
            resolved_player,
            round_num,
            death_tick,
        )
        if damage_before_death is None:
            missing_features.append("damage_before_death")

        if first_player_kill_tick is None:
            survived_after_first_kill = False if kills_before_death is not None else None
        elif death_tick is None:
            survived_after_first_kill = True
        else:
            survived_after_first_kill = death_tick > first_player_kill_tick
        if survived_after_first_kill is None:
            missing_features.append("survived_after_first_kill")

        utility_used_before_death = _utility_used_before_death(
            frames["grenades"],
            frames["shots"],
            resolved_player,
            round_num,
            death_tick,
        )
        if utility_used_before_death is None:
            missing_features.append("utility_used_before_death")

        round_win = _round_win(frames["rounds"], side, round_num)
        if round_win is None:
            missing_features.append("round_win")

        alive_features, alive_missing = _alive_context_features(
            frames["ticks"],
            frames["kills"],
            resolved_player,
            side,
            round_num,
            death_tick,
        )
        missing_features.extend(alive_missing)

        feature_row = {
            "round": round_num,
            "player_name": resolved_player,
            "kills": kills,
            "deaths": deaths,
            "damage_dealt": damage_dealt,
            "flashes_thrown": utility_counts["flashes_thrown"],
            "smokes_thrown": utility_counts["smokes_thrown"],
            "molotovs_incendiaries_thrown": utility_counts["molotovs_incendiaries_thrown"],
            "he_grenades_thrown": utility_counts["he_grenades_thrown"],
            "utility_count": utility_count,
            "survived_round": survived_round,
            "died_first": died_first,
            "death_tick": death_tick,
            "death_time": death_time,
            "side": side,
            "team": team,
            "opening_kill": opening_kill,
            "opening_death": opening_death,
            "kills_before_death": kills_before_death,
            "damage_before_death": damage_before_death,
            "clutch_situation": alive_features["clutch_situation"],
            "survived_after_first_kill": survived_after_first_kill,
            "utility_used_before_death": utility_used_before_death,
            "round_win": round_win,
            "team_alive_when_player_died": alive_features["team_alive_when_player_died"],
            "enemies_alive_when_player_died": alive_features["enemies_alive_when_player_died"],
            "missing_features": sorted(set(missing_features)),
        }
        results.append(feature_row)

    return results


def summarize_missing_features(features: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in features:
        counter.update(row.get("missing_features", []))
    return dict(sorted(counter.items()))


