"""Simple deterministic engine model used for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
import copy
from typing import Any, ClassVar

from engine.engine_base import EngineBase, BaseEngineState

@dataclass
class SimpleEngineState(BaseEngineState):
	def __init__(self, initState: dict[str, Any] | None = None):
		initState = initState or {}
		super().__init__()
		self.air_mass = 1.0 if initState.get("air_mass") is None else float(initState["air_mass"])
		self.fuel_mass = 0.05 if initState.get("fuel_mass") is None else float(initState["fuel_mass"])
		self.engine_speed_rpm = (
			900.0 if initState.get("engine_speed_rpm") is None else float(initState["engine_speed_rpm"])
		)
		self.torque = 0.0 if initState.get("torque") is None else float(initState["torque"])


@dataclass
class SimpleEngine(EngineBase):
	"""Small fixed-parameter engine model.

	The constants are intentionally explicit so they can later move into YAML
	configuration without changing the simulation code path.
	"""

	required_sensors: ClassVar[frozenset[str]] = frozenset({"AFR_sensor"})

	air_inflow_coeff: float
	air_outflow_coeff: float
	fuel_burn_coeff: float
	torque_coeff: float
	load_coeff: float
	speed_response_coeff: float
	init_state: dict[str, object] = field(default_factory=dict)
	state: BaseEngineState = field(init=False)
	_initial_state: BaseEngineState = field(init=False, repr=False)

	def __post_init__(self) -> None:
		self.state = SimpleEngineState(self.init_state)
		self._initial_state = copy.deepcopy(self.state)

	def reset(self) -> None:
		self.state = copy.deepcopy(self._initial_state)

	def step(self, throttle: float, fuel_injection: float, dt: float) -> BaseEngineState:
		next_state = copy.deepcopy(self.state)
		air_inflow = self.air_inflow_coeff * throttle
		air_outflow = self.air_outflow_coeff * next_state.air_mass
		next_state.air_mass = max(0.0, next_state.air_mass + dt * (air_inflow - air_outflow))

		fuel_burn = self.fuel_burn_coeff * next_state.fuel_mass
		next_state.fuel_mass = max(0.0, next_state.fuel_mass + dt * (fuel_injection - fuel_burn))

		torque_from_fuel = self.torque_coeff * fuel_injection
		load_torque = self.load_coeff * next_state.engine_speed_rpm
		# allow negative net torque (engine absorbing torque / braking)
		net_torque = torque_from_fuel - load_torque
		next_state.torque = net_torque
  
		# RPM responds to the net torque (positive accelerates, negative decelerates)
		rpm_delta = self.speed_response_coeff * net_torque
		next_state.engine_speed_rpm = max(0.0, next_state.engine_speed_rpm + dt * rpm_delta)

		self.state = next_state
		return next_state

