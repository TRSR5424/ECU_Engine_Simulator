"""Configuration validation for engine, sensor, and ECU compatibility."""

from __future__ import annotations

from collections.abc import Iterable

from typing import cast, Any

class ConfigurationValidationError(ValueError):
    """Raised when a runtime configuration is internally incompatible."""


def _as_sequence(sensors) -> list[object]:
	"""Normalize the input into the expected representation."""
	# Configuration accepts one sensor or a collection so callers do not need
	# special-case logic for single-sensor experiments.
	if sensors is None:
		return []

	if isinstance(sensors, (str, bytes)):
		return [sensors]

	if isinstance(sensors, Iterable):
		return list(sensors)

	return [sensors]

def _has_map(engine) -> bool:
	"""Report whether the requested capability is available."""
	return bool(getattr(engine, "fuel_map", None))



def _format_block(title: str, name: str, missing: set[str], available: set[str] | None = None) -> str:
	"""Format the requested values for user-facing output."""
	lines = ["Configuration Error", title, name, "Missing"]
	for item in sorted(missing):
		lines.append(f"- {item}")

	if available is not None:
		lines.append("Available")
		for item in sorted(available):
			lines.append(f"- {item}")

	return "\n".join(lines)


def validate(engine, sensors, ecu) -> None:
	"""Validate that the selected engine, sensors, and ECU are compatible."""

	installed_sensors = _as_sequence(sensors)
	installed_sensor_types = {
		sensor.sensorType() for sensor in installed_sensors
	}

	required_sensors = {
		str(sensor_name)
		for sensor_name in getattr(engine, "required_sensors", frozenset())
	}
	missing_sensors = required_sensors.difference(installed_sensor_types)
	if missing_sensors:
		raise ConfigurationValidationError(
			_format_block(
				"Engine",
				engine.__class__.__name__,
				missing_sensors,
				installed_sensor_types,
			)
		)

	available_signals: set[str] = set()
	for sensor in installed_sensors:
		# Sensor implementations expose this legacy method dynamically; retain
		# the cast at this compatibility boundary rather than changing the API.
		sensor = cast(Any, sensor)
		provided_signal = sensor.providedSignal()
		available_signals.update(str(provided_signal).lower() for provided_signal in _as_sequence(provided_signal))

	required_signals = {
		str(signal).lower()
		for signal in getattr(ecu, "required_signals", frozenset())
	}
	missing_signals = required_signals.difference(available_signals)
	if missing_signals:
		raise ConfigurationValidationError(
			_format_block(
				"ECU",
				ecu.__class__.__name__,
				missing_signals,
				available_signals,
			)
		)

	map_required = getattr(ecu, "engine_map", False)
	if map_required and not _has_map(engine):
		raise ConfigurationValidationError(
			_format_block(
				"ECU",
				ecu.__class__.__name__,
				{"engine_map"},
				{"no engine map was provided"},
			)
		)
