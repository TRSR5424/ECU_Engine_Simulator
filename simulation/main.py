#!/usr/bin/env python3
"""CLI entry point for the fixed-parameter MVP simulation."""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from simulation.logger import CsvLogger
from simulation.simulator import Simulator


def main() -> None:
    simulator = Simulator()
    result = simulator.run()

    CsvLogger().write("data/simulation_output.csv", result.records)

    final_record = result.records[-1]
    print(
        "Simulation complete: "
        f"t={final_record.time:.2f}s, "
        f"rpm={final_record.engine_speed_rpm:.1f}, "
        f"afr={final_record.air_fuel_ratio:.2f}"
    )

if __name__ == '__main__':
    main()
