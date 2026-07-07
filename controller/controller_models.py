"""Controller metadata models used for validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


class ControllerModelBase:
    """Shared metadata for controller implementations."""

    required_signals: ClassVar[frozenset[str]] = frozenset()


@dataclass(frozen=True)
class FixedControllerModel(ControllerModelBase):
    """Metadata for the fixed-output controller."""

    required_signals: ClassVar[frozenset[str]] = frozenset({"air_fuel_ratio"})


@dataclass(frozen=True)
class PIDControllerModel(ControllerModelBase):
    """Metadata for the PID controller."""

    required_signals: ClassVar[frozenset[str]] = frozenset({"air_fuel_ratio"})