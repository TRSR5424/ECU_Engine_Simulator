"""Sensor variant that returns a delayed reading history."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from sensor.sensor_base import SensorBase

@dataclass
class DelayedSensor(SensorBase):
	# Number of simulation steps to delay the reading.
	delay_steps: int = 1
	_history: deque[float] = field(init=False, repr=False)

	def __post_init__(self) -> None:
		if self.delay_steps < 0:
			raise ValueError("delay_steps must be non-negative")
		history_length = self.delay_steps
		self._history = deque([0.0] * history_length, maxlen=history_length + 1)

	def reset(self) -> None:
		self._history.clear()
		self._history.extend([0.0] * self.delay_steps)

	def read(self, actual_state: float) -> float:
		if not self._history.maxlen:
			return actual_state

		self._history.append(actual_state)
		return self._history[0]
