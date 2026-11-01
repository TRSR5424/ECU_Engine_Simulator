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
from simulation.invariants import validate_controller_output, validate_engine_state
from simulation.input_schedule import InputSchedule
from simulation.timestep_loop import calculate_step_count


from engine.engine_base import BaseEngineState

@dataclass(frozen=True)
class SimulationSettings:
    """Represent the SimulationSettings component used by the simulator."""
    duration: float = 30.0
    dt: float = 0.1
    throttle: float | dict[Any, Any] = 0.6
    target_air_fuel_ratio: float | dict[Any, Any] = 14.7
    load_torque: float | dict[Any, Any] = 0.0

    def __post_init__(self) -> None:
        """Validate and finalize dataclass initialization."""
        calculate_step_count(self.duration, self.dt)
        InputSchedule(self.throttle, "throttle", 0.0, 1.0)
        InputSchedule(self.target_air_fuel_ratio, "target_air_fuel_ratio", 0.0, None, strict_minimum=True)
        InputSchedule(self.load_torque, "load_torque", 0.0, None)
    
@dataclass()
class SimulationState:
    """Represent the SimulationState component used by the simulator."""
    engine_state: BaseEngineState
    initial_engine_state: BaseEngineState = field(repr=False)
    current_time: float = 0.0
    step_index: int = 0
    started: bool = False
    
@dataclass
class SimulationResult:
    """Represent the SimulationResult component used by the simulator."""
    records: list[SimulationRecord] = field(default_factory=list)


def _resolve_sensor_values(sensors: list[SensorBase], state: BaseEngineState) -> dict[str, float]:
    """Resolve the requested runtime values from the current state."""
    sensor_values = {}
    state_dict = state.__dict__

    for sensor in sensors:
        # AFR is derived rather than stored in the state dataclass, so it needs
        # an explicit lookup before ordinary state fields are considered.
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
    """Represent the Simulator component used by the simulator."""
    state: SimulationState = field(init=False)
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    engine: EngineBase = field(default_factory=create_engine)
    controller: ControllerBridge = field(default_factory=ControllerBridge)
    sensors: list[SensorBase] = field(default_factory=create_sensors)
    input_schedule: dict[str, InputSchedule] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate and finalize dataclass initialization."""
        self.input_schedule = {
            "throttle": InputSchedule(self.settings.throttle, "throttle", 0.0, 1.0),
            "target_air_fuel_ratio": InputSchedule(
                self.settings.target_air_fuel_ratio,
                "target_air_fuel_ratio",
                0.0,
                strict_minimum=True,
            ),
            "load_torque": InputSchedule(self.settings.load_torque, "load_torque", 0.0),
        }
        initial_engine_state = copy.deepcopy(self.engine.state)
        self.state = SimulationState(
            engine_state=self.engine.state,
            initial_engine_state=initial_engine_state,
        )
        self.reset()

    @property
    def finished(self) -> bool:
        """Report whether all configured simulation steps are complete."""
        return self.state.step_index >= calculate_step_count(self.settings.duration, self.settings.dt)

    def _simulation_step(self, timestep_index: int, timestep_time: float, previous_state: BaseEngineState) -> SimulationRecord:
        """Perform the internal helper operation represented by this function."""
        # Sensors read the pre-transition state; the resulting record stores
        # the post-transition engine state alongside those measurements.
        throttle = self.input_schedule["throttle"].resolve(timestep_index)
        target_air_fuel_ratio = self.input_schedule["target_air_fuel_ratio"].resolve(timestep_index)
        load_torque = self.input_schedule["load_torque"].resolve(timestep_index)
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
        validate_controller_output(fuel_injection)

        state = self.engine.step(
            throttle=throttle,
            fuel_injection=fuel_injection,
            dt=self.settings.dt,
            load_torque=load_torque,
        )
        validate_engine_state(state)

        measured_air_fuel_ratio = measured_values.get("air_fuel_ratio", state.air_fuel_ratio)

        record = SimulationRecord(
            time=timestep_time,
            throttle=throttle,
            load_torque=load_torque,
            fuel_injection=fuel_injection,
            air_mass=state.air_mass,
            fuel_mass=state.fuel_mass,
            air_fuel_ratio=state.air_fuel_ratio,
            target_air_fuel_ratio=target_air_fuel_ratio,
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
        """Run the configured operation to completion and return its result."""
        result = SimulationResult()

        while not self.finished:
            result.records.append(self.step())

        return result
