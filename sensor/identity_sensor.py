from __future__ import annotations

from dataclasses import dataclass

from sensor.sensor_base import SensorBase

@dataclass
class IdentitySensor(SensorBase):
    """Identity sensor used by the default simulation configuration."""

    # Calibration multiplier applied to the measured value.
    scale: float = 1.0
    # Constant calibration offset added after scaling.
    offset: float = 0.0

    def read(self, actual_state: float) -> float:
        return actual_state * self.scale + self.offset
