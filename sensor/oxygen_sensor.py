"""Oxygen sensor implementations built on the generic sensor behaviors."""

from __future__ import annotations

from dataclasses import dataclass

from sensor.identity_sensor import IdentitySensor
from sensor.noisy_sensor import NoisySensor
from sensor.delayed_sensor import DelayedSensor
from sensor.sensor_base import Sensor


@dataclass
class OxygenSensor(Sensor):
    sensor_type = "oxygen_sensor"
    provided_signal = "air_fuel_ratio"


@dataclass
class OxygenIdentitySensor(IdentitySensor):
    sensor_type = "oxygen_sensor"
    provided_signal = "air_fuel_ratio"


@dataclass
class OxygenNoisySensor(NoisySensor):
    sensor_type = "oxygen_sensor"
    provided_signal = "air_fuel_ratio"


@dataclass
class OxygenDelayedSensor(DelayedSensor):
    sensor_type = "oxygen_sensor"
    provided_signal = "air_fuel_ratio"