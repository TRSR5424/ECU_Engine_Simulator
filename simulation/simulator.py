"""Core fixed-parameter simulation loop for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.simple_engine import SimpleEngine
from simulation.logger import SimulationRecord
from simulation.timestep_loop import iter_timesteps


@dataclass(frozen=True)
class SimulationSettings:
    duration: float = 5.0
    dt: float = 0.1
    throttle: float = 0.6
    fuel_injection: float = 0.08


@dataclass
class SimulationResult:
    records: list[SimulationRecord] = field(default_factory=list)


@dataclass
class Simulator:
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    engine: SimpleEngine = field(default_factory=SimpleEngine)

    def run(self) -> SimulationResult:
        result = SimulationResult()

        for timestep in iter_timesteps(self.settings.duration, self.settings.dt):
            state = self.engine.step(
                throttle=self.settings.throttle,
                fuel_injection=self.settings.fuel_injection,
                dt=self.settings.dt,
            )
            result.records.append(
                SimulationRecord(
                    time=timestep.time,
                    throttle=self.settings.throttle,
                    fuel_injection=self.settings.fuel_injection,
                    air_mass=state.air_mass,
                    fuel_mass=state.fuel_mass,
                    air_fuel_ratio=state.air_fuel_ratio,
                    engine_speed_rpm=state.engine_speed_rpm,
                    torque=state.torque,
                )
            )

        return result

