from __future__ import annotations

from typing import Any


class MapConfigError(RuntimeError):
    """Raised when a map has no configured radar transform."""


# Radar transform fields mirror CS radar metadata:
# pos_x/pos_y are the upper-left world coordinate, scale is world-units per pixel.
# Add a new map by dropping its image into static/maps/ and adding an entry here.
map_configs: dict[str, dict[str, Any]] = {
    "de_ancient": {
        "image": "/static/maps/de_ancient_radar.png",
        "pos_x": -2953,
        "pos_y": 2164,
        "scale": 5.0,
    },
    "de_cache": {
        "image": "/static/maps/de_cache_radar.png",
        "pos_x": -2000,
        "pos_y": 3250,
        "scale": 5.5,
    },
    "de_dust2": {
        "image": "/static/maps/de_dust2_radar.png",
        "pos_x": -2476,
        "pos_y": 3239,
        "scale": 4.4,
    },
    "de_inferno": {
        "image": "/static/maps/de_inferno_radar.png",
        "pos_x": -2087,
        "pos_y": 3870,
        "scale": 4.9,
    },
    "de_mirage": {
        "image": "/static/maps/de_mirage_radar.png",
        "pos_x": -3230,
        "pos_y": 1713,
        "scale": 5.0,
    },
    "de_nuke": {
        "image": "/static/maps/de_nuke_radar.png",
        "lower_image": "/static/maps/de_nuke_lower_radar.png",
        "pos_x": -3453,
        "pos_y": 2887,
        "scale": 7.0,
    },
    "de_overpass": {
        "image": "/static/maps/de_overpass_radar.png",
        "pos_x": -4831,
        "pos_y": 1781,
        "scale": 5.2,
    },
    "de_train": {
        "image": "/static/maps/de_train_radar.png",
        "pos_x": -2477,
        "pos_y": 2392,
        "scale": 4.7,
    },
    "de_vertigo": {
        "image": "/static/maps/de_vertigo_radar.png",
        "lower_image": "/static/maps/de_vertigo_lower_radar.png",
        "pos_x": -3168,
        "pos_y": 1762,
        "scale": 4.0,
    },
}


def get_map_config(map_name: str | None) -> dict[str, Any] | None:
    if not map_name:
        return None
    return map_configs.get(str(map_name))


def world_to_map(map_name: str, world_x: float, world_y: float, world_z: float | None = None) -> dict[str, float | None]:
    """
    Convert CS2 world coordinates to radar-image pixel coordinates.

    All replay coordinate conversion should go through this helper so future
    map calibration changes stay centralized.
    """
    config = get_map_config(map_name)
    if config is None:
        raise MapConfigError(f"No map config exists for map '{map_name}'.")

    scale = float(config["scale"])
    return {
        "x": (float(world_x) - float(config["pos_x"])) / scale,
        "y": (float(config["pos_y"]) - float(world_y)) / scale,
        "z": world_z,
    }
