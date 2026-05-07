"""Helpers for advancing a simulation in fixed timesteps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Timestep:
	time: float
	index: int


def iter_timesteps(duration: float, dt: float) -> Iterator[Timestep]:
	"""Yield the timesteps covered by a fixed-duration simulation."""

	if dt <= 0.0:
		raise ValueError("dt must be greater than zero")

	steps = max(1, int(duration / dt))
	for index in range(steps):
		yield Timestep(time=index * dt, index=index)

