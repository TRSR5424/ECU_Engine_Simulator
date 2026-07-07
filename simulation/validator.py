"""Configuration validation for engine, sensor, and ECU compatibility."""

from __future__ import annotations

from collections.abc import Iterable


class ConfigurationValidationError(ValueError):
    """Raised when a runtime configuration is internally incompatible."""


def _as_sequence(sensors) -> list[object]:
	if sensors is None:
		return []

	if isinstance(sensors, (str, bytes)):
		return [sensors]

	if isinstance(sensors, Iterable):
		return list(sensors)

	return [sensors]


def _format_block(title: str, name: str, missing: set[str], available: set[str] | None = None) -> str:
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
		str(getattr(sensor, "sensor_type", sensor.__class__.__name__)).lower()
		for sensor in installed_sensors
	}

	required_sensors = {
		str(sensor_name).lower()
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
		provided_signals = getattr(sensor, "provided_signals", frozenset())
		available_signals.update(str(signal) for signal in provided_signals)

	required_signals = {
		str(signal).lower()
		for signal in getattr(ecu, "required_signals", frozenset())
	}
	available_signal_names = {signal.lower() for signal in available_signals}
	missing_signals = required_signals.difference(available_signal_names)
	if missing_signals:
		raise ConfigurationValidationError(
			_format_block(
				"ECU",
				ecu.__class__.__name__,
				missing_signals,
				available_signal_names,
			)
		)