"""Factory helpers for sensor implementations."""

from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import Any

from sensor.delayed_sensor import DelayedSensor
from sensor.noisy_sensor import NoisySensor
from sensor.identity_sensor import IdentitySensor
from sensor.afr_sensor import AFRDelayedSensor
from sensor.afr_sensor import AFRIdentitySensor
from sensor.afr_sensor import AFRNoisySensor
from sensor.afr_sensor import AFRSensor
from sensor.sensor_base import SensorBase
from sensor.sensor_base import Sensor


_SENSOR_TYPES: dict[str, type[SensorBase]] = {
	"actual": Sensor,
	"AFR_sensor": AFRSensor,
	"identity": IdentitySensor,
	"AFR_identity": AFRIdentitySensor,
	"noisy": NoisySensor,
	"AFR_noisy": AFRNoisySensor,
	"delayed": DelayedSensor,
	"AFR_delayed": AFRDelayedSensor,
}


def create_sensors(config: dict[str, Any] | None = None) -> list[SensorBase]:
	"""Build a sensor instance from a runtime config mapping."""

	sensor_config = config.copy() if config is not None else {}
 
	if sensor_config == {}:
		raise ValueError("Sensor factory requires a non-empty configuration dictionary")
 
	sensors = []
 
	for sensor in sensor_config.values():
		sensor_type_name = str(sensor["type"])

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
    
		sensors.append(sensor_type(**filtered_config))

	return sensors
