"""CSV logging helpers for simulation output."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from simulation.config_resolver import RuntimeConfig


@dataclass(frozen=True)
class SimulationRecord:
	time: float
	throttle: float
	load_torque: float
	fuel_injection: float
	air_mass: float
	fuel_mass: float
	air_fuel_ratio: float
	measured_air_fuel_ratio: float
	engine_speed_rpm: float
	torque: float


class CsvLogger:
	"""Persist simulation records to a CSV file."""

	def __init__(self, run_config: RuntimeConfig):
		self.run_config = run_config

	header = [
		"time",
		"throttle",
		"load_torque",
		"fuel_injection",
		"air_mass",
		"fuel_mass",
		"air_fuel_ratio",
		"measured_air_fuel_ratio",
		"engine_speed_rpm",
		"torque",
	]

	def write(self, path: str | Path, records: Iterable[SimulationRecord]) -> Path:
		output_path = Path(path, f"{self.run_config.active_experiment}/.{self.run_config.active_experiment}_output.csv")
		output_path.parent.mkdir(parents=True, exist_ok=True)
  
		information_path = output_path.with_suffix(".info.txt")
  
		with information_path.open("w", encoding="utf-8") as info_handle:
			info_handle.write(f"Active Experiment: {self.run_config.active_experiment}\n")
			info_handle.write(f"Output CSV: {output_path}\n")
   
			info_handle.write("\nConfiguration Information:\n")
			# Duration and timestep
			info_handle.write(f"  Simulation Duration (seconds): {self.run_config.simulation['duration_seconds']}\n")
			info_handle.write(f"  Simulation Timestep (seconds): {self.run_config.simulation['timestep_seconds']}\n")
			# Engine configuration
			info_handle.write(f"  Engine Configuration:\n")
			for key, value in self.run_config.engine.items():
				info_handle.write(f"    {key}: {value}\n")
			# Controller configuration
			info_handle.write(f"  Controller Configuration:\n")
			for key, value in self.run_config.controller.items():
				info_handle.write(f"    {key}: {value}\n")
			# Sensor configuration
			info_handle.write(f"  Sensor Configuration:\n")
			for key, value in self.run_config.sensor.items():
				info_handle.write(f"    {key}: {value}\n")

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
						record.engine_speed_rpm,
						record.torque,
					]
				)

		return output_path

