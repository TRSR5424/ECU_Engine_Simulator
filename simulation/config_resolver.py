"""YAML configuration loading and merge helpers for the simulator MVP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load the configured defaults required by the component."""
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    if loaded is None:
        return {}

    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}, got {type(loaded).__name__}")

    return loaded


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Perform the internal helper operation represented by this function."""
    merged = dict(base)
    for key, value in override.items():
        # Nested mappings are merged so an experiment can override one field
        # without duplicating the rest of the base configuration.
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@dataclass(frozen=True)
class RuntimeConfig:
    """Represent the RuntimeConfig component used by the simulator."""
    project: str
    active_experiment: str
    simulation: dict[str, Any]
    logging: dict[str, Any]
    engine: dict[str, Any]
    controller: dict[str, Any]
    scenario: dict[str, Any]
    reference: dict[str, Any]
    sensor: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Run the to dict operation."""
        return {
            "project": self.project,
            "active_experiment": self.active_experiment,
            "simulation": self.simulation,
            "logging": self.logging,
            "engine": self.engine,
            "controller": self.controller,
            "scenario": self.scenario,
            "reference": self.reference,
            "sensor": self.sensor,
        }


def load_runtime_config(config_root: str | Path = "config") -> RuntimeConfig:
    """Run the load runtime config operation."""
    root = Path(config_root)

    global_config = _load_yaml(root / "global.yaml")

    # Global settings select the experiment-specific model files; simulation
    # timing and logging remain global defaults for every experiment.
    config_folder = global_config.get("config_folder", "base")

    engine_config = _load_yaml(root / config_folder / "engine.yaml")
    controller_config = _load_yaml(root / config_folder / "controller.yaml")
    scenario_config = _load_yaml(root / config_folder / "scenario.yaml")
    reference_config = _load_yaml(root / config_folder / "reference.yaml")
    sensor_config = _load_yaml(root / config_folder / "sensor.yaml")

    simulation_config = global_config.get("simulation", {})
    logging_config = global_config.get("logging", {})

    return RuntimeConfig(
        project=global_config.get("project", "engine-control-sim"),
        active_experiment=global_config.get("active_experiment", "default"),
        simulation={
            "duration_seconds": float(simulation_config.get("duration_seconds", 30.0)),
            "timestep_seconds": float(simulation_config.get("timestep_seconds", 0.1)),
        },
        logging={
            "output_csv": str(logging_config.get("output_csv", "data/{active_experiment}/")),
        },
        engine=engine_config,
        controller=controller_config,
        scenario=scenario_config,
        reference=reference_config,
        sensor=sensor_config,
    )


def write_resolved_config(runtime_config: RuntimeConfig, output_path: str | Path) -> Path:
    """Run the write resolved config operation."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(runtime_config.to_dict(), handle, sort_keys=False)

    return path
