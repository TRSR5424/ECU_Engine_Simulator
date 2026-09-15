"""Runtime checks for physically and numerically valid simulation states."""

from __future__ import annotations

import math

from engine.engine_base import BaseEngineState


class SimulationError(RuntimeError):
    """Raised when a simulation transition violates a runtime invariant."""


def validate_engine_state(state: BaseEngineState) -> None:
    """Validate the physical state produced by an engine transition.

    An AFR of positive infinity is allowed only when fuel mass is zero; this
    represents an undefined ratio rather than a numerical failure.
    """
    for name in ("air_mass", "fuel_mass", "engine_speed_rpm", "torque"):
        value = getattr(state, name)
        if not math.isfinite(value):
            raise SimulationError(f"{name} became non-finite")

    if state.air_mass < 0.0:
        raise SimulationError("air mass became negative")
    if state.fuel_mass < 0.0:
        raise SimulationError("fuel mass became negative")
    if state.engine_speed_rpm < 0.0:
        raise SimulationError("engine speed became negative")

    air_fuel_ratio = state.air_fuel_ratio
    if state.fuel_mass > 0.0 and not math.isfinite(air_fuel_ratio):
        raise SimulationError("air-fuel ratio became non-finite")
    if air_fuel_ratio < 0.0:
        raise SimulationError("air-fuel ratio became negative")


def validate_controller_output(fuel_injection: float) -> None:
    """Ensure the engine receives a finite, non-negative fuel command."""
    if not math.isfinite(fuel_injection) or fuel_injection < 0.0:
        raise SimulationError("controller produced an invalid fuel injection")
