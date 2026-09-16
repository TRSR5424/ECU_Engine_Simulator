"""Validated step-based input schedules for simulation scenarios."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real
from typing import Any


@dataclass(frozen=True)
class InputSchedule:
    """Resolve a constant or step-based numeric input."""

    value: float | dict[Any, Any]
    name: str
    minimum: float
    maximum: float | None = None
    strict_minimum: bool = False

    def __post_init__(self) -> None:
        values = {"-1": self.value} if not isinstance(self.value, dict) else self.value
        normalized_keys: list[int] = []
        for raw_step, raw_value in values.items():
            try:
                step = int(raw_step)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{self.name} schedule keys must be integers") from exc
            if step < -1:
                raise ValueError(f"{self.name} schedule keys must be -1 or greater")
            normalized_keys.append(step)
            if not isinstance(raw_value, Real) or isinstance(raw_value, bool):
                raise ValueError(f"{self.name} schedule values must be numeric")
            numeric_value = float(raw_value)
            below_minimum = (
                numeric_value <= self.minimum
                if self.strict_minimum
                else numeric_value < self.minimum
            )
            if not math.isfinite(numeric_value) or below_minimum:
                comparison = "greater than" if self.strict_minimum else "at least"
                raise ValueError(
                    f"{self.name} schedule values must be finite and {comparison} {self.minimum}"
                )
            if self.maximum is not None and numeric_value > self.maximum:
                raise ValueError(
                    f"{self.name} schedule values must be at most {self.maximum}"
                )

        if any(step != -1 for step in normalized_keys) and 0 not in normalized_keys:
            raise ValueError(
                f"{self.name} schedules with timed keys must include step 0"
            )

    def resolve(self, step_index: int) -> float:
        """Return the active value at a simulation step."""
        if not isinstance(self.value, dict):
            return float(self.value)

        resolved_value: float | None = None
        for raw_step, raw_value in sorted(self.value.items(), key=lambda item: int(item[0])):
            if int(raw_step) <= step_index:
                resolved_value = float(raw_value)
            else:
                break

        if resolved_value is None:
            raise ValueError(f"{self.name} schedule has no value for step {step_index}")
        return resolved_value
