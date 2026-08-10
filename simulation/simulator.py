"""Core fixed-parameter simulation loop for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from controller.bindings.controller_bridge import ControllerBridge, ControllerInput
from engine.engine_base import EngineBase
from engine.engine_factory import create_engine
from sensor.sensor_base import SensorBase
from sensor.sensor_factory import create_sensors
from simulation.logger import SimulationRecord
from simulation.timestep_loop import iter_timesteps

from engine.engine_base import BaseEngineState


@dataclass(frozen=True)
class SimulationSettings:
    duration: float = 30.0
    dt: float = 0.1
    throttle: float | dict[Any, Any] = 0.6
    target_air_fuel_ratio: float | dict[Any, Any] = 14.7


@dataclass
class SimulationResult:
    records: list[SimulationRecord] = field(default_factory=list)


def _resolve_scheduled_value(value: float | dict[Any, Any], step_index: int, default: float) -> float:
    if not isinstance(value, dict):
        return float(value)

    normalized_keys = {int(raw_step) for raw_step in value}
    if any(step_key != -1 for step_key in normalized_keys) and 0 not in normalized_keys:
        raise ValueError("Scheduled values with time-based keys must include step 0")

    resolved_value = float(default)
    for raw_step, raw_value in sorted(value.items(), key=lambda item: int(item[0])):
        if int(raw_step) <= step_index:
            resolved_value = float(raw_value)
        else:
            break

    return resolved_value

def _resolve_sensor_values(sensors: list[SensorBase], state: BaseEngineState) -> dict[str, float]:
    sensor_values = {}
    state_dict = state.__dict__
    
    for sensor in sensors:
        if sensor.provided_signal == "air_fuel_ratio":
            sensor_values["air_fuel_ratio"] = sensor.read(state.air_fuel_ratio)
            break
        
        for item, value in state_dict.items():
            if sensor.provided_signal == item:
                sensor_values[item] = sensor.read(value)
                break
    
    return sensor_values


@dataclass
class Simulator:
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    engine: EngineBase = field(default_factory=create_engine)
    controller: ControllerBridge = field(default_factory=ControllerBridge)
    sensors: list[SensorBase] = field(default_factory=create_sensors)

    def run(self) -> SimulationResult:
        result = SimulationResult()

        # get initial state record before stepping the simulation
        initial_state = self.engine.state
        state = initial_state
        measured_values = _resolve_sensor_values(self.sensors, state)
        throttle = _resolve_scheduled_value(self.settings.throttle, 0, 0.6)
        target_air_fuel_ratio = _resolve_scheduled_value(
            self.settings.target_air_fuel_ratio,
            0,
            14.7,
        )

        for timestep in iter_timesteps(self.settings.duration, self.settings.dt):
            throttle = _resolve_scheduled_value(
                self.settings.throttle,
                timestep.index,
                0.6,
            )
            target_air_fuel_ratio = _resolve_scheduled_value(
                self.settings.target_air_fuel_ratio,
                timestep.index,
                14.7,
            )
            fuel_injection = self.controller.compute(
                ControllerInput(
                    time_seconds=timestep.time,
                    throttle_position=throttle,
                    target_air_fuel_ratio=target_air_fuel_ratio,
                    measured_values=measured_values,
                    engine_speed_rpm=state.engine_speed_rpm,
                    torque=state.torque,
                    air_mass=state.air_mass,
                    fuel_mass=state.fuel_mass,
                )
            )

            state = self.engine.step(
                throttle=throttle,
                fuel_injection=fuel_injection,
                dt=self.settings.dt,
            )

            measured_air_fuel_ratio = measured_values.get("air_fuel_ratio", state.air_fuel_ratio)

            result.records.append(
                SimulationRecord(
                    time=timestep.time,
                    throttle=throttle,
                    fuel_injection=fuel_injection,
                    air_mass=state.air_mass,
                    fuel_mass=state.fuel_mass,
                    air_fuel_ratio=state.air_fuel_ratio,
                    measured_air_fuel_ratio=measured_air_fuel_ratio,
                    engine_speed_rpm=state.engine_speed_rpm,
                    torque=state.torque,
                )
            )

        return result

