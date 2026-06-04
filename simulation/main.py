#!/usr/bin/env python3
"""CLI entry point for the fixed-parameter MVP simulation."""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from controller.bindings.controller_bridge import ControllerBridge
from engine.simple_engine import SimpleEngine
from sensor.sensor_base import Sensor
from simulation.config_resolver import load_runtime_config, write_resolved_config
from simulation.logger import CsvLogger
from simulation.simulator import Simulator
from simulation.simulator import SimulationSettings


def main() -> None:
    runtime_config = load_runtime_config()
    write_resolved_config(runtime_config, Path("config/active/resolved_config.yaml"))

    simulation_settings = SimulationSettings(
        duration=runtime_config.simulation["duration_seconds"],
        dt=runtime_config.simulation["timestep_seconds"],
        throttle=float(runtime_config.scenario.get("throttle", 0.6)),
        target_air_fuel_ratio=float(runtime_config.reference.get("target_air_fuel_ratio", 14.7)),
    )

    engine = SimpleEngine(**{key: value for key, value in runtime_config.engine.items() if key != "name"})
    sensor = Sensor()
    controller = ControllerBridge(config=runtime_config.controller)
    simulator = Simulator(settings=simulation_settings, engine=engine, controller=controller, sensor=sensor)
    result = simulator.run()

    CsvLogger().write(runtime_config.logging["output_csv"], result.records)

    final_record = result.records[-1]
    print(
        "Simulation complete: "
        f"t={final_record.time:.2f}s, "
        f"rpm={final_record.engine_speed_rpm:.1f}, "
        f"afr={final_record.air_fuel_ratio:.2f}"
    )

if __name__ == '__main__':
    main()
