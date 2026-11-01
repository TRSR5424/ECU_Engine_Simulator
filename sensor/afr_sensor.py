"""AFR sensor implementations built on the generic sensor behaviors."""

from __future__ import annotations

from dataclasses import dataclass

from sensor.identity_sensor import IdentitySensor
from sensor.noisy_sensor import NoisySensor
from sensor.delayed_sensor import DelayedSensor
from sensor.sensor_base import Sensor


@dataclass
class AFRSensor(Sensor):
    """Represent the AFRSensor component used by the simulator."""
    sensor_type = "AFR_sensor"
    provided_signal = "air_fuel_ratio"


@dataclass
class AFRIdentitySensor(IdentitySensor):
    """Represent the AFRIdentitySensor component used by the simulator."""
    sensor_type = "AFR_sensor"
    provided_signal = "air_fuel_ratio"


@dataclass
class AFRNoisySensor(NoisySensor):
    """Represent the AFRNoisySensor component used by the simulator."""
    sensor_type = "AFR_sensor"
    provided_signal = "air_fuel_ratio"


@dataclass
class AFRDelayedSensor(DelayedSensor):
    """Represent the AFRDelayedSensor component used by the simulator."""
    sensor_type = "AFR_sensor"
    provided_signal = "air_fuel_ratio"
