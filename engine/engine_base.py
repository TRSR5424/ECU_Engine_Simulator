"""Shared engine model types and interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class BaseEngineState:
    """State tracked by the simplified engine model."""
    
    air_mass: float = 1.0
    fuel_mass: float = 0.05
    engine_speed_rpm: float = 900.0
    torque: float = 0.0

    @property
    def air_fuel_ratio(self) -> float:
        if self.fuel_mass <= 0.0:
            return float("inf")
        return self.air_mass / self.fuel_mass


class EngineBase(ABC):
    """Interface for future engine implementations."""

    state: BaseEngineState
    required_sensors: ClassVar[frozenset[str]] = frozenset()
    
    def __init__(self) -> None:
        self.state = BaseEngineState()

    @abstractmethod
    def step(
        self,
        throttle: float,
        fuel_injection: float,
        dt: float,
        load_torque: float = 0.0,
    ) -> BaseEngineState:
        """Advance the engine state by one timestep."""

    @abstractmethod
    def reset(self) -> None:
        """Restore the engine to its initial physical state."""


EngineState = BaseEngineState

