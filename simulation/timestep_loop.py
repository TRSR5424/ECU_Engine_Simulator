"""Helpers for advancing a simulation in fixed timesteps."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterator


@dataclass(frozen=True)
class Timestep:
	time: float
	index: int


def iter_timesteps(duration: float, dt: float) -> Iterator[Timestep]:
	"""Yield the timesteps covered by a fixed-duration simulation."""
	steps = calculate_step_count(duration, dt)
	for index in range(steps):
		yield Timestep(time=index * dt, index=index)


def calculate_step_count(duration: float, dt: float) -> int:
	"""Return the number of transitions for an exact fixed timestep run."""
	if duration <= 0.0:
		raise ValueError("duration must be greater than zero")
	if dt <= 0.0:
		raise ValueError("dt must be greater than zero")

	steps = round(duration / dt)
	if not math.isclose(steps * dt, duration, rel_tol=0.0, abs_tol=1e-12):
		raise ValueError("duration must be an integer multiple of dt")
	return steps

