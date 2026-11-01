"""CSV logging helpers for simulation output."""

from __future__ import annotations

import csv
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from simulation.config_resolver import RuntimeConfig
from simulation.timestep_loop import calculate_step_count


@dataclass(frozen=True)
class SimulationRecord:
	"""Represent the SimulationRecord component used by the simulator."""
	time: float
	throttle: float
	load_torque: float
	fuel_injection: float
	air_mass: float
	fuel_mass: float
	air_fuel_ratio: float
	target_air_fuel_ratio: float
	measured_air_fuel_ratio: float
	engine_speed_rpm: float
	torque: float


class CsvLogger:
	"""Persist simulation records to a CSV file."""

	def __init__(self, run_config: RuntimeConfig):
		"""Initialize the component and its runtime state."""
		self.run_config = run_config

	@staticmethod
	def _git_revision() -> str | None:
		"""Run the  git revision operation."""
		try:
			result = subprocess.run(
				["git", "rev-parse", "HEAD"],
				capture_output=True,
				check=True,
				text=True,
			)
		except (OSError, subprocess.CalledProcessError):
			return None
		return result.stdout.strip() or None

	@staticmethod
	def _state_values(state) -> dict[str, float]:
		"""Run the  state values operation."""
		return {
			"air_mass": state.air_mass,
			"fuel_mass": state.fuel_mass,
			"engine_speed_rpm": state.engine_speed_rpm,
			"torque": state.torque,
			"air_fuel_ratio": state.air_fuel_ratio,
		}

	def _build_info(self, simulator, records: list[SimulationRecord], output_path: Path) -> dict:
		"""Run the  build info operation."""
		final_record = records[-1] if records else None
		sensor_details = []
		for name, sensor in self.run_config.sensor.items():
			if isinstance(sensor, dict):
				sensor_details.append(
					{
						"name": name,
						"type": sensor.get("type"),
						"seed": sensor.get("seed"),
						"noise_stddev": sensor.get("noise_stddev"),
						"delay_steps": sensor.get("delay_steps"),
					}
				)

		return {
			"provenance": {
				"git_revision": self._git_revision(),
				"project": self.run_config.project,
				"active_experiment": self.run_config.active_experiment,
				"resolved_configuration": "config/active/resolved_config.yaml",
			},
			"timing": {
				"duration_seconds": self.run_config.simulation["duration_seconds"],
				"timestep_seconds": self.run_config.simulation["timestep_seconds"],
				"expected_steps": calculate_step_count(simulator.settings.duration, simulator.settings.dt),
				"recorded_steps": len(records),
			},
			"models": {
				"engine": type(simulator.engine).__name__,
				"controller": type(simulator.controller).__name__,
				"sensors": sensor_details,
			},
			"inputs": {
				"schedules": {
					name: schedule.value
					for name, schedule in simulator.input_schedule.items()
				},
			},
			"randomness": {
				"sensor_seeds": [sensor["seed"] for sensor in sensor_details],
				"deterministic": all(
					sensor["seed"] is not None
					for sensor in sensor_details
					if sensor["noise_stddev"] is not None
				),
			},
			"state": {
				"initial": self._state_values(simulator.state.initial_engine_state),
				"final": self._state_values(simulator.state.engine_state),
			},
			"result": {
				"output_csv": str(output_path),
				"final_record": vars(final_record) if final_record is not None else None,
			},
		}

	header = [
		"time",
		"throttle",
		"load_torque",
		"fuel_injection",
		"air_mass",
		"fuel_mass",
		"air_fuel_ratio",
		"target_air_fuel_ratio",
		"measured_air_fuel_ratio",
		"engine_speed_rpm",
		"torque",
	]

	def write(self, path: str | Path, records: Iterable[SimulationRecord], simulator=None) -> Path:
		"""Run the write operation."""
		records = list(records)
		output_path = Path(path, f"{self.run_config.active_experiment}/.{self.run_config.active_experiment}_output.csv")
		output_path.parent.mkdir(parents=True, exist_ok=True)
  
		information_path = output_path.with_suffix(".info.yaml")
  
		if simulator is not None:
			info = self._build_info(simulator, records, output_path)
		else:
			info = {
				"info_format": 2,
				"provenance": {
					"project": self.run_config.project,
					"active_experiment": self.run_config.active_experiment,
				},
				"result": {"output_csv": str(output_path)},
			}
		with information_path.open("w", encoding="utf-8") as info_handle:
			yaml.safe_dump(info, info_handle, sort_keys=False)

		with output_path.open("w", newline="", encoding="utf-8") as handle:
			writer = csv.writer(handle)
			writer.writerow(self.header)
			for record in records:
				writer.writerow(
					[
						record.time,
						record.throttle,
						record.load_torque,
						record.fuel_injection,
						record.air_mass,
						record.fuel_mass,
						record.air_fuel_ratio,
						record.measured_air_fuel_ratio,
						record.target_air_fuel_ratio,
						record.engine_speed_rpm,
						record.torque,
					]
				)

		return output_path

