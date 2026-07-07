"""Shared sensor interfaces and the default fixed sensor implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class SensorBase(ABC):
    """Interface for sensor implementations."""

    sensor_type: str = "sensor"
    provided_signals: frozenset[str] = frozenset()

    @abstractmethod
    def read(self, actual_state: float) -> float:
        """Return a measured value for the provided state."""
        raise NotImplementedError("Sensor implementations must override the read method.")


@dataclass
class Sensor(SensorBase):
    def read(self, actual_state: float) -> float:
        return actual_state
