from __future__ import annotations

from pathlib import Path
from typing import Any

from awpy import Demo


class DemoParseError(RuntimeError):
    """Raised when Awpy cannot parse a demo or returns an unexpected shape."""


KNOWN_PARSED_ATTRIBUTES = (
    "header",
    "rounds",
    "kills",
    "damages",
    "grenades",
    "bomb",
    "smokes",
    "infernos",
    "shots",
    "ticks",
)


def _public_attributes(obj: Any) -> list[str]:
    return sorted(name for name in dir(obj) if not name.startswith("_"))


def _describe_available_data(demo: Any) -> str:
    pieces: list[str] = []
    for attr in KNOWN_PARSED_ATTRIBUTES:
        if not hasattr(demo, attr):
            continue

        value = getattr(demo, attr)
        columns = getattr(value, "columns", None)
        shape = getattr(value, "shape", None)
        if columns is not None:
            pieces.append(f"{attr}(columns={list(columns)}, shape={shape})")
        else:
            pieces.append(f"{attr}(type={type(value).__name__})")

    if pieces:
        return "; ".join(pieces)

    return f"public attributes={_public_attributes(demo)}"


def parse_demo(path: str) -> Any:
    """
    Parse a real Counter-Strike 2 .dem file with Awpy.

    Awpy's Demo.parse() populates properties such as rounds, kills, damages,
    grenades and ticks on the Demo instance. This function returns that parsed
    Demo object directly so later stages can inspect the real parser output.
    """
    demo_path = Path(path)
    if not demo_path.exists():
        raise DemoParseError(f"Demo file does not exist: {demo_path}")

    try:
        dem = Demo(str(demo_path))
        parse_result = dem.parse()
    except Exception as exc:
        raise DemoParseError(f"Awpy failed to parse '{demo_path.name}': {exc}") from exc

    if parse_result is not None and not any(hasattr(dem, attr) for attr in KNOWN_PARSED_ATTRIBUTES):
        # Some parser versions may return useful data from parse(); keep it
        # attached for debugging without replacing the requested Demo object.
        setattr(dem, "_parse_result", parse_result)

    available = _describe_available_data(dem)
    if not any(hasattr(dem, attr) for attr in ("rounds", "kills", "damages", "grenades", "ticks")):
        raise DemoParseError(
            "Awpy parse completed, but no expected parsed data attributes were found. "
            f"Available data: {available}"
        )

    rounds = getattr(dem, "rounds", None)
    if rounds is not None and hasattr(rounds, "height") and rounds.height == 0:
        raise DemoParseError(
            "Awpy parse completed, but the rounds dataframe is empty. "
            f"Available data: {available}"
        )

    return dem
