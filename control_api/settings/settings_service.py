from __future__ import annotations

from pathlib import Path
from typing import Any

from control_api._service_utils import CONFIG_ROOT, deep_merge, load_global_config, load_yaml, write_yaml


SECTION_NAMES = ("engine", "controller", "scenario", "reference", "sensor")


def _experiment_root(experiment_name: str) -> Path:
    return CONFIG_ROOT / experiment_name


def _load_experiment_settings(experiment_name: str) -> dict[str, Any]:
    experiment_root = _experiment_root(experiment_name)
    if not experiment_root.exists():
        raise FileNotFoundError(f"Unknown experiment '{experiment_name}'")

    return {
        section_name: load_yaml(experiment_root / f"{section_name}.yaml")
        for section_name in SECTION_NAMES
    }


def _recursive_diff(before: Any, after: Any, *, path: str = "") -> list[dict[str, Any]]:
    if isinstance(before, dict) and isinstance(after, dict):
        differences: list[dict[str, Any]] = []
        keys = sorted(set(before) | set(after))
        for key in keys:
            child_path = f"{path}.{key}" if path else str(key)
            if key not in before:
                differences.append({"path": child_path, "before": None, "after": after[key]})
            elif key not in after:
                differences.append({"path": child_path, "before": before[key], "after": None})
            else:
                differences.extend(_recursive_diff(before[key], after[key], path=child_path))
        return differences

    if before != after:
        return [{"path": path or "value", "before": before, "after": after}]

    return []


def get_settings(config_name: str | None = None) -> dict[str, Any]:
    global_settings = load_global_config()
    active_experiment = global_settings.get("config_folder", global_settings.get("active_experiment", "base"))

    if config_name is None:
        return {
            "global": global_settings,
            "active_experiment": active_experiment,
            "experiment_settings": _load_experiment_settings(active_experiment),
        }

    if config_name in SECTION_NAMES:
        return {
            "config_name": config_name,
            "experiment": active_experiment,
            "settings": load_yaml(_experiment_root(active_experiment) / f"{config_name}.yaml"),
        }

    if config_name in {"global", "global.yaml"}:
        return {"config_name": "global", "settings": global_settings}

    experiment_settings = _load_experiment_settings(config_name)
    return {
        "config_name": config_name,
        "settings": experiment_settings,
    }


def create_new_experiment(experiment_name: str, experiment_settings: dict[str, dict]):
    experiment_root = _experiment_root(experiment_name)
    if experiment_root.exists():
        raise FileExistsError(f"Experiment '{experiment_name}' already exists")

    created_files = []
    for section_name, section_settings in experiment_settings.items():
        if not isinstance(section_settings, dict):
            raise ValueError(f"Expected a mapping for '{section_name}' settings")
        created_files.append(str(write_yaml(experiment_root / f"{section_name}.yaml", section_settings)))

    return {
        "experiment": experiment_name,
        "created_files": created_files,
        "message": "Experiment created successfully!",
    }


def update_settings(experiment_name: str, new_settings: dict[str, dict]):
    current_settings = _load_experiment_settings(experiment_name)
    experiment_root = _experiment_root(experiment_name)

    updated_files: list[str] = []
    for section_name, section_settings in new_settings.items():
        if not isinstance(section_settings, dict):
            raise ValueError(f"Expected a mapping for '{section_name}' settings")

        merged_settings = deep_merge(current_settings.get(section_name, {}), section_settings)
        updated_files.append(str(write_yaml(experiment_root / f"{section_name}.yaml", merged_settings)))

    return {
        "experiment": experiment_name,
        "updated_files": updated_files,
        "message": "Settings updated successfully!",
    }


def update_global_settings(new_settings: dict[str, str]):
    global_settings = load_global_config()
    merged_settings = deep_merge(global_settings, new_settings)
    write_yaml(CONFIG_ROOT / "global.yaml", merged_settings)

    return {
        "new_settings": new_settings,
        "settings": merged_settings,
        "message": "Global settings updated successfully!",
    }


def compare_settings(experiment_name: str):
    global_settings = load_global_config()
    active_experiment = global_settings.get("config_folder", global_settings.get("active_experiment", "base"))
    active_settings = _load_experiment_settings(active_experiment)
    comparison_settings = _load_experiment_settings(experiment_name)

    differences = {
        section_name: _recursive_diff(active_settings.get(section_name, {}), comparison_settings.get(section_name, {}))
        for section_name in SECTION_NAMES
    }

    return {
        "source_experiment": active_experiment,
        "comparison_experiment": experiment_name,
        "differences": differences,
        "has_differences": any(differences.values()),
    }


def set_compare(value: bool):
    global_settings = load_global_config()
    updated_settings = deep_merge(global_settings, {"comparison": {"enabled": bool(value)}})
    write_yaml(CONFIG_ROOT / "global.yaml", updated_settings)

    return {
        "compare": bool(value),
        "settings": updated_settings.get("comparison", {}),
        "message": "Compare mode updated successfully!",
    }