"""Shared sensor interfaces and the default fixed sensor implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class SensorBase(ABC):
    """Interface for sensor implementations."""

    @abstractmethod
    def read(self, actual_state: float) -> float:
        """Return a measured value for the provided state."""


@dataclass
class Sensor(SensorBase):
    """Identity sensor used by the default simulation configuration."""

    # Calibration multiplier applied to the measured value.
    scale: float = 1.0
    # Constant calibration offset added after scaling.
    offset: float = 0.0

    def read(self, actual_state: float) -> float:
        return actual_state * self.scale + self.offset
