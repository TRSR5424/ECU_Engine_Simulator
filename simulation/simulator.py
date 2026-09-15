"""Core fixed-parameter simulation loop for the MVP."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from controller.bindings.controller_bridge import ControllerBridge, ControllerInput
from engine.engine_base import EngineBase
from engine.engine_factory import create_engine
from sensor.sensor_base import SensorBase
from sensor.sensor_factory import create_sensors
from simulation.logger import SimulationRecord
from simulation.timestep_loop import calculate_step_count


from engine.engine_base import BaseEngineState

@dataclass(frozen=True)
class SimulationSettings:
    duration: float = 30.0
    dt: float = 0.1
    throttle: float | dict[Any, Any] = 0.6
    target_air_fuel_ratio: float | dict[Any, Any] = 14.7
    
@dataclass()
class SimulationState:
    engine_state: BaseEngineState
    initial_engine_state: BaseEngineState = field(repr=False)
    current_time: float = 0.0
    step_index: int = 0
    started: bool = False
    
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
    state: SimulationState = field(init=False)
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    engine: EngineBase = field(default_factory=create_engine)
    controller: ControllerBridge = field(default_factory=ControllerBridge)
    sensors: list[SensorBase] = field(default_factory=create_sensors)

    def __post_init__(self) -> None:
        initial_engine_state = copy.deepcopy(self.engine.state)
        self.state = SimulationState(
            engine_state=self.engine.state,
            initial_engine_state=initial_engine_state,
        )
        self.reset()

    @property
    def finished(self) -> bool:
        return self.state.step_index >= calculate_step_count(self.settings.duration, self.settings.dt)

    def _simulation_step(self, timestep_index: int, timestep_time: float, previous_state: BaseEngineState) -> SimulationRecord:
        throttle = _resolve_scheduled_value(
            self.settings.throttle,
            timestep_index,
            0.6,
        )
        target_air_fuel_ratio = _resolve_scheduled_value(
            self.settings.target_air_fuel_ratio,
            timestep_index,
            14.7,
        )
        measured_values = _resolve_sensor_values(self.sensors, previous_state)
        fuel_injection = self.controller.compute(
            ControllerInput(
                time_seconds=timestep_time,
                throttle_position=throttle,
                target_air_fuel_ratio=target_air_fuel_ratio,
                measured_values=measured_values,
                engine_speed_rpm=previous_state.engine_speed_rpm,
                torque=previous_state.torque,
                air_mass=previous_state.air_mass,
                fuel_mass=previous_state.fuel_mass,
            )
        )

        state = self.engine.step(
            throttle=throttle,
            fuel_injection=fuel_injection,
            dt=self.settings.dt,
        )

        measured_air_fuel_ratio = measured_values.get("air_fuel_ratio", state.air_fuel_ratio)

        record = SimulationRecord(
            time=timestep_time,
            throttle=throttle,
            fuel_injection=fuel_injection,
            air_mass=state.air_mass,
            fuel_mass=state.fuel_mass,
            air_fuel_ratio=state.air_fuel_ratio,
            measured_air_fuel_ratio=measured_air_fuel_ratio,
            engine_speed_rpm=state.engine_speed_rpm,
            torque=state.torque,
        )

        return record

    def reset(self) -> None:
        """Restore the engine and simulator clock to their construction state."""
        self.engine.reset()
        self.controller.reset()
        for sensor in self.sensors:
            sensor.reset()
        self.state.engine_state = self.engine.state
        self.state.current_time = 0.0
        self.state.step_index = 0
        self.state.started = False

    def step(self) -> SimulationRecord:
        """Advance exactly one transition and return its resulting record."""
        if self.finished:
            raise RuntimeError("simulation is already finished")

        record = self._simulation_step(self.state.step_index, self.state.current_time, self.engine.state)
        self.state.engine_state = self.engine.state
        self.state.step_index += 1
        self.state.current_time += self.settings.dt
        self.state.started = True
        return record

    def run_stepwise(self) -> tuple[SimulationResult, bool]:
        """Run one transition for compatibility with the legacy CLI."""
        result = SimulationResult()
        if not self.finished:
            result.records.append(self.step())
        return result, self.finished
    
    def run(self) -> SimulationResult:
        result = SimulationResult()

        while not self.finished:
            result.records.append(self.step())

        return result