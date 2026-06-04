"""Sensor variant that adds repeatable Gaussian noise to readings."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from sensor.sensor_base import SensorBase


@dataclass
class NoisySensor(SensorBase):
	# Standard deviation of the Gaussian measurement noise.
	noise_stddev: float = 0.01
	# Random seed used to make the noise repeatable.
	seed: int | None = None
	_random: Random = field(init=False, repr=False)

	def __post_init__(self) -> None:
		self._random = Random(self.seed)

	def read(self, actual_state: float) -> float:
		return actual_state + self._random.gauss(0.0, self.noise_stddev)
