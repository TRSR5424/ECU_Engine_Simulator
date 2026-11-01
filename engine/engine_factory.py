"""Factory helpers for engine implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from engine.engine_base import EngineBase
from engine.simple_engine import SimpleEngine


_ENGINE_TYPES: dict[str, type[EngineBase]] = {
	"simple_engine": SimpleEngine,
}


def _load_engine_defaults() -> dict[str, Any]:
	"""Load the configured defaults required by the component."""
	config_path = Path("config/base/engine.yaml")
	if not config_path.exists():
		return {}

	with config_path.open("r", encoding="utf-8") as handle:
		loaded_config = yaml.safe_load(handle) or {}

	if not isinstance(loaded_config, dict):
		raise ValueError(f"Expected mapping in {config_path}, got {type(loaded_config).__name__}")

	return loaded_config


def create_engine(config: dict[str, Any] | None = None) -> EngineBase:
	"""Build an engine instance from a runtime config mapping."""

	engine_config = _load_engine_defaults()
	engine_config.update(dict(config or {}))
	engine_name = str(engine_config.pop("name", "simple_engine"))

	try:
		engine_type = _ENGINE_TYPES[engine_name]
	except KeyError as exc:
		available_types = ", ".join(sorted(_ENGINE_TYPES))
		raise ValueError(
			f"Unknown engine type '{engine_name}'. Available types: {available_types}"
		) from exc

	return engine_type(**engine_config)
