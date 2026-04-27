import os
from pathlib import Path

import yaml


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(config_path: str | Path | None = None) -> dict:
    if config_path is None:
        config_path = get_project_root() / "config" / "config.yaml"
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as handle:
        base_config = yaml.safe_load(handle)

    env_prefix = "SPOT_MONITORING_"
    overrides = {}
    for key, value in os.environ.items():
        if not key.startswith(env_prefix):
            continue
        path = key[len(env_prefix) :].lower().split("__")
        target = overrides
        for part in path[:-1]:
            target = target.setdefault(part, {})
        target[path[-1]] = yaml.safe_load(value)

    merged = _deep_merge_dicts(base_config, overrides)
    return merged


def _deep_merge_dicts(base: dict, overrides: dict) -> dict:
    result = dict(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
