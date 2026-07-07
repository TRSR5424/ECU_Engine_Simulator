"""Simple deterministic engine model used for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from engine.engine_base import EngineBase, EngineState


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
	state: EngineState = field(default_factory=EngineState)

	def step(self, throttle: float, fuel_injection: float, dt: float) -> EngineState:
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

