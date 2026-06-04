"""Factory helpers for sensor implementations."""

from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import Any

from sensor.delayed_sensor import DelayedSensor
from sensor.noisy_sensor import NoisySensor
from sensor.identity_sensor import IdentitySensor
from sensor.sensor_base import SensorBase
from sensor.sensor_base import Sensor


_SENSOR_TYPES: dict[str, type[SensorBase]] = {
	"actual": Sensor,
	"identity": IdentitySensor,
	"noisy": NoisySensor,
	"delayed": DelayedSensor,
}


def create_sensor(config: dict[str, Any] | None = None) -> SensorBase:
	"""Build a sensor instance from a runtime config mapping."""

	sensor_config = dict(config or {})
	sensor_type_name = str(sensor_config.pop("type", "fixed"))

	sensor_type = _SENSOR_TYPES.get(sensor_type_name)
	if sensor_type is None:
		available_types = ", ".join(sorted(_SENSOR_TYPES))
		raise ValueError(
			f"Unknown sensor type '{sensor_type_name}'. Available types: {available_types}"
		)

	if not is_dataclass(sensor_type):
		raise TypeError(f"Sensor type '{sensor_type.__name__}' must be a dataclass")

	valid_fields = [field for field in fields(sensor_type) if field.init]
	valid_keys = {field.name for field in valid_fields}

	filtered_config: dict[str, Any] = {}
	for field in valid_fields:
		if field.name in sensor_config:
			filtered_config[field.name] = sensor_config[field.name]
			continue

		if field.default is not MISSING:
			default_value = field.default
		else:
			default_value = None

		print(
			f"Sensor factory: missing config key '{field.name}' for {sensor_type.__name__}, "
			f"using the default value {default_value!r}."
		)

	for key, value in sensor_config.items():
		if key in valid_keys:
			filtered_config[key] = value
		else:
			default_value = getattr(sensor_type, key, None)
			print(
				f"Sensor factory: unknown config key '{key}' for {sensor_type.__name__}, "
				f"ignoring it and using the default value {default_value!r}."
			)

	return sensor_type(**filtered_config)
