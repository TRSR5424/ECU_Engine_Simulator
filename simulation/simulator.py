"""Core fixed-parameter simulation loop for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field

from controller.bindings.controller_bridge import ControllerBridge, ControllerInput
from engine.simple_engine import SimpleEngine
from simulation.logger import SimulationRecord
from simulation.timestep_loop import iter_timesteps


@dataclass(frozen=True)
class SimulationSettings:
    duration: float = 30.0
    dt: float = 0.1
    throttle: float = 0.6
    target_air_fuel_ratio: float = 14.7


@dataclass
class SimulationResult:
    records: list[SimulationRecord] = field(default_factory=list)


@dataclass
class Simulator:
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    engine: SimpleEngine = field(default_factory=SimpleEngine)
    controller: ControllerBridge = field(default_factory=ControllerBridge)

    def run(self) -> SimulationResult:
        result = SimulationResult()

        # get initial state record before stepping the simulation
        initial_state = self.engine.state
        state = initial_state
        result.records.append(
            SimulationRecord(
                time=0.0,
                throttle=self.settings.throttle,
                fuel_injection=self.controller.compute(
                    ControllerInput(
                        time_seconds=0.0,
                        throttle_position=self.settings.throttle,
                        target_air_fuel_ratio=self.settings.target_air_fuel_ratio,
                        measured_air_fuel_ratio=initial_state.air_fuel_ratio,
                        engine_speed_rpm=initial_state.engine_speed_rpm,
                        torque=initial_state.torque,
                        air_mass=initial_state.air_mass,
                        fuel_mass=initial_state.fuel_mass,
                    )
                ),
                air_mass=initial_state.air_mass,
                fuel_mass=initial_state.fuel_mass,
                air_fuel_ratio=initial_state.air_fuel_ratio,
                engine_speed_rpm=initial_state.engine_speed_rpm,
                torque=initial_state.torque,
            )
        )

        for timestep in iter_timesteps(self.settings.duration, self.settings.dt):
            fuel_injection = self.controller.compute(
                ControllerInput(
                    time_seconds=timestep.time,
                    throttle_position=self.settings.throttle,
                    target_air_fuel_ratio=self.settings.target_air_fuel_ratio,
                    measured_air_fuel_ratio=state.air_fuel_ratio,
                    engine_speed_rpm=state.engine_speed_rpm,
                    torque=state.torque,
                    air_mass=state.air_mass,
                    fuel_mass=state.fuel_mass,
                )
            )
            
            state = self.engine.step(
                throttle=self.settings.throttle,
                fuel_injection=fuel_injection,
                dt=self.settings.dt,
            )
            result.records.append(
                SimulationRecord(
                    time=timestep.time,
                    throttle=self.settings.throttle,
                    fuel_injection=fuel_injection,
                    air_mass=state.air_mass,
                    fuel_mass=state.fuel_mass,
                    air_fuel_ratio=state.air_fuel_ratio,
                    engine_speed_rpm=state.engine_speed_rpm,
                    torque=state.torque,
                )
            )

        return result

