from __future__ import annotations

from pathlib import Path
from typing import Any

from controller.bindings.controller_bridge import ControllerBridge
from engine.engine_factory import create_engine
from sensor.sensor_factory import create_sensor
from simulation.config_resolver import load_runtime_config, write_resolved_config
from simulation.logger import CsvLogger
from simulation.simulator import SimulationSettings, Simulator

from control_api._service_utils import DATA_ROOT, list_experiment_names


def _active_experiment_folder() -> Path:
    runtime_config = load_runtime_config()
    return DATA_ROOT / runtime_config.active_experiment


def _run_simulation() -> dict[str, Any]:
    runtime_config = load_runtime_config()
    write_resolved_config(runtime_config, Path("config/active/resolved_config.yaml"))

    simulation_settings = SimulationSettings(
        duration=runtime_config.simulation["duration_seconds"],
        dt=runtime_config.simulation["timestep_seconds"],
        throttle=runtime_config.scenario.get("throttle", 0.6),
        target_air_fuel_ratio=runtime_config.scenario.get("target_air_fuel_ratio", 14.7),
    )

    engine = create_engine(runtime_config.engine)
    sensor = create_sensor(runtime_config.sensor)
    controller = ControllerBridge(config=runtime_config.controller)
    simulator = Simulator(settings=simulation_settings, engine=engine, controller=controller, sensor=sensor)
    result = simulator.run()

    csv_path = CsvLogger(run_config=runtime_config).write(runtime_config.logging["output_csv"], result.records)
    final_record = result.records[-1] if result.records else None

    return {
        "script": "simulation",
        "status": "completed",
        "records": len(result.records),
        "output_csv": str(csv_path),
        "final_record": None
        if final_record is None
        else {
            "time": final_record.time,
            "throttle": final_record.throttle,
            "fuel_injection": final_record.fuel_injection,
            "air_mass": final_record.air_mass,
            "fuel_mass": final_record.fuel_mass,
            "air_fuel_ratio": final_record.air_fuel_ratio,
            "measured_air_fuel_ratio": final_record.measured_air_fuel_ratio,
            "engine_speed_rpm": final_record.engine_speed_rpm,
            "torque": final_record.torque,
        },
    }


def _run_analysis() -> dict[str, Any]:
    from analysis.run_analysis import save_single

    runtime_config = load_runtime_config()
    experiment_folder = _active_experiment_folder()
    save_single(str(experiment_folder))

    return {
        "script": "analysis",
        "status": "completed",
        "experiment": runtime_config.active_experiment,
        "output_folder": str(experiment_folder),
    }


def _run_comparison() -> dict[str, Any]:
    from analysis.compare_runs import compare

    runtime_config = load_runtime_config()
    active_folder = _active_experiment_folder()
    experiment_names = [name for name in list_experiment_names() if name != runtime_config.active_experiment]

    if not experiment_names:
        return {
            "script": "compare_runs",
            "status": "skipped",
            "reason": "No comparison experiment was found.",
            "experiment": runtime_config.active_experiment,
        }

    other_experiment = experiment_names[0]
    other_folder = DATA_ROOT / other_experiment
    compare(str(active_folder), str(other_folder))

    return {
        "script": "compare_runs",
        "status": "completed",
        "experiment_a": runtime_config.active_experiment,
        "experiment_b": other_experiment,
    }


def get_scripts() -> dict[str, Any]:
    runtime_config = load_runtime_config()
    return {
        "scripts": [
            {
                "name": "simulation",
                "description": "Run the simulator using the active configuration and write a CSV output.",
            },
            {
                "name": "analysis",
                "description": "Generate plots and a report for the active experiment output.",
            },
            {
                "name": "compare_runs",
                "description": "Compare the active experiment against another available experiment folder.",
            },
        ],
        "active_experiment": runtime_config.active_experiment,
    }


def run_script(script_name: str) -> dict[str, Any]:
    normalized_name = script_name.strip().lower()

    if normalized_name in {"simulation", "simulation/main.py", "run_simulation"}:
        return _run_simulation()

    if normalized_name in {"analysis", "analysis/run_analysis.py", "run_analysis"}:
        return _run_analysis()

    if normalized_name in {"compare_runs", "compare", "analysis/compare_runs.py"}:
        return _run_comparison()

    return {
        "script": script_name,
        "status": "unknown-script",
        "available_scripts": ["simulation", "analysis", "compare_runs"],
    }


def run_all_scripts() -> dict[str, Any]:
    results = [run_script(script_name) for script_name in ("simulation", "analysis", "compare_runs")]
    return {"scripts": results}