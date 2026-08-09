"""Simple deterministic engine model used for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
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

	required_sensors: ClassVar[frozenset[str]] = frozenset({"oxygen_sensor"})

	air_inflow_coeff: float
	air_outflow_coeff: float
	fuel_burn_coeff: float
	torque_coeff: float
	load_coeff: float
	speed_response_coeff: float
	init_state: dict[str, object] = field(default_factory=dict)
	state: BaseEngineState = field(init=False)

	def __post_init__(self) -> None:
		self.state = SimpleEngineState(self.init_state)

	def step(self, throttle: float, fuel_injection: float, dt: float) -> BaseEngineState:
		air_inflow = self.air_inflow_coeff * throttle
		air_outflow = self.air_outflow_coeff * self.state.air_mass
		self.state.air_mass = max(0.0, self.state.air_mass + dt * (air_inflow - air_outflow))

		fuel_burn = self.fuel_burn_coeff * self.state.fuel_mass
		self.state.fuel_mass = max(0.0, self.state.fuel_mass + dt * (fuel_injection - fuel_burn))

		torque_from_fuel = self.torque_coeff * fuel_injection
		load_torque = self.load_coeff * self.state.engine_speed_rpm
		# allow negative net torque (engine absorbing torque / braking)
		net_torque = torque_from_fuel - load_torque
		self.state.torque = net_torque
  
		# RPM responds to the net torque (positive accelerates, negative decelerates)
		rpm_delta = self.speed_response_coeff * net_torque
		self.state.engine_speed_rpm = max(0.0, self.state.engine_speed_rpm + dt * rpm_delta)

		return self.state

