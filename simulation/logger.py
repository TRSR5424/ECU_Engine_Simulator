"""CSV logging helpers for simulation output."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SimulationRecord:
	time: float
	throttle: float
	fuel_injection: float
	air_mass: float
	fuel_mass: float
	air_fuel_ratio: float
	measured_air_fuel_ratio: float
	engine_speed_rpm: float
	torque: float


class CsvLogger:
	"""Persist simulation records to a CSV file."""

	header = [
		"time",
		"throttle",
		"fuel_injection",
		"air_mass",
		"fuel_mass",
		"air_fuel_ratio",
		"measured_air_fuel_ratio",
		"engine_speed_rpm",
		"torque",
	]

	def write(self, path: str | Path, records: Iterable[SimulationRecord]) -> Path:
		output_path = Path(path)
		output_path.parent.mkdir(parents=True, exist_ok=True)

		with output_path.open("w", newline="", encoding="utf-8") as handle:
			writer = csv.writer(handle)
			writer.writerow(self.header)
			for record in records:
				writer.writerow(
					[
						record.time,
						record.throttle,
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

