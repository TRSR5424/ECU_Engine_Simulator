from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import csv
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = REPO_ROOT / "config"
DATA_ROOT = REPO_ROOT / "data"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    if loaded is None:
        return {}

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a mapping in {path}, got {type(loaded).__name__}")

    return loaded


def write_yaml(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
    return path


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def collect_config_files(experiment_name: str) -> dict[str, dict[str, Any]]:
    experiment_root = CONFIG_ROOT / experiment_name
    if not experiment_root.exists():
        raise FileNotFoundError(f"Unknown experiment '{experiment_name}'")

    return {
        name: load_yaml(experiment_root / f"{name}.yaml")
        for name in ("engine", "controller", "scenario", "reference", "sensor")
    }


def load_global_config() -> dict[str, Any]:
    return load_yaml(CONFIG_ROOT / "global.yaml")


def list_experiment_names() -> list[str]:
    ignored = {"active", "base"}
    if not CONFIG_ROOT.exists():
        return []

    names = [entry.name for entry in CONFIG_ROOT.iterdir() if entry.is_dir() and entry.name not in ignored]
    return sorted(names)


def read_csv_preview(csv_path: Path, limit: int = 10) -> dict[str, Any]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for index, row in enumerate(reader):
            if index >= limit:
                break
            rows.append(row)

    return {
        "path": str(csv_path),
        "rows": rows,
    }


def list_matching_files(folder: Path, suffixes: Iterable[str]) -> list[Path]:
    if not folder.exists():
        return []

    suffix_set = {suffix.lower() for suffix in suffixes}
    files = [entry for entry in folder.iterdir() if entry.is_file() and entry.suffix.lower() in suffix_set]
    return sorted(files)
