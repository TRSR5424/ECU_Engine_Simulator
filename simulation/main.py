#!/usr/bin/env python3
"""CLI entry point for the fixed-parameter MVP simulation."""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from controller.bindings.controller_bridge import ControllerBridge
from engine.engine_factory import create_engine
from sensor.sensor_factory import create_sensors
from simulation.config_resolver import load_runtime_config, write_resolved_config
from simulation.logger import CsvLogger
from simulation.simulator import Simulator
from simulation.simulator import SimulationSettings
from simulation.simulator import SimulationResult
from simulation.validator import validate

class Main:
    """Main entry point for the fixed-parameter MVP simulation."""

    def __init__(self) -> None:
        self.running_simulation = False
        self.is_step = False

    async def start(self) -> None:
        self.running_simulation = True

    async def stop(self) -> None:
        self.running_simulation = False
        
    async def toggle(self) -> None:
        self.running_simulation = not self.running_simulation
        
    async def step(self) -> None:
        self.running_simulation = True
        await self.stop()

    def main(self) -> None:
        runtime_config = load_runtime_config()
        write_resolved_config(runtime_config, Path("config/active/resolved_config.yaml"))

        method = runtime_config.simulation.get("run_mode", "full")

        simulation_settings = SimulationSettings(
            duration=runtime_config.simulation["duration_seconds"],
            dt=runtime_config.simulation["timestep_seconds"],
            throttle=runtime_config.scenario.get("throttle", 0.6),
            target_air_fuel_ratio=runtime_config.scenario.get("target_air_fuel_ratio", 14.7),
        )

        engine = create_engine(runtime_config.engine)
        sensors = create_sensors(runtime_config.sensor)
        controller = ControllerBridge(config=runtime_config.controller)
        validate(engine, sensors, controller)
        simulator = Simulator(settings=simulation_settings, engine=engine, controller=controller, sensors=sensors)

        result: SimulationResult = SimulationResult()
        match method:
            case "stepwise":
                timesteps = None
                while self.running_simulation or self.is_step:
                    result, timesteps, end = simulator.run_stepwise(timesteps=timesteps)
                    self.is_step = False
                    if end:
                        break
                        
            case "stepwise_terminal":
                timesteps = None
                while True:
                    result, timesteps, end = simulator.run_stepwise(timesteps=timesteps)
                    if end:
                        break
                    
                    print(result)
                    input("Press Enter to continue to the next step...")
                    
            case "full":
                result = simulator.run()
            case _:
                raise ValueError(f"Unknown run_mode: {method}")

        CsvLogger(run_config=runtime_config).write(runtime_config.logging["output_csv"], result.records)

        final_record = result.records[-1]
        print(
            "Simulation complete: "
            f"t={final_record.time:.2f}s, "
            f"rpm={final_record.engine_speed_rpm:.1f}, "
            f"afr={final_record.air_fuel_ratio:.2f}"
        )

if __name__ == '__main__':
    main = Main()
    main.main()
