"""Shared sensor interfaces and the default fixed sensor implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class SensorBase(ABC):
    """Interface for sensor implementations."""

    sensor_type: str = "sensor"
    provided_signal: str = ""

    @abstractmethod
    def read(self, actual_state: float) -> float:
        """Return a measured value for the provided state."""
        raise NotImplementedError("Sensor implementations must override the read method.")

    def reset(self) -> None:
        """Restore sensor runtime state to its initial condition."""
    
    def sensorType(self) -> str:
        """Return the type of this sensor."""
        return self.sensor_type
    
    def providedSignal(self) -> str:
        """Return the name of the signal provided by this sensor."""
        return self.provided_signal

@dataclass
class Sensor(SensorBase):
    def read(self, actual_state: float) -> float:
        return actual_state
