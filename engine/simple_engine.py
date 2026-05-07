"""Simple deterministic engine model used for the MVP."""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.engine_base import EngineBase, EngineState


@dataclass
class SimpleEngine(EngineBase):
	"""Small fixed-parameter engine model.

	The constants are intentionally explicit so they can later move into YAML
	configuration without changing the simulation code path.
	"""

	air_inflow_coeff: float = 1.5
	air_outflow_coeff: float = 0.25
	fuel_burn_coeff: float = 0.4
	torque_coeff: float = 180.0
	load_coeff: float = 0.02
	speed_response_coeff: float = 0.04
	state: EngineState = field(default_factory=EngineState)

	def step(self, throttle: float, fuel_injection: float, dt: float) -> EngineState:
		air_inflow = self.air_inflow_coeff * throttle
		air_outflow = self.air_outflow_coeff * self.state.air_mass
		self.state.air_mass = max(0.0, self.state.air_mass + dt * (air_inflow - air_outflow))

		fuel_burn = self.fuel_burn_coeff * self.state.fuel_mass
		self.state.fuel_mass = max(0.0, self.state.fuel_mass + dt * (fuel_injection - fuel_burn))

		torque_from_fuel = self.torque_coeff * fuel_injection
		load_torque = self.load_coeff * self.state.engine_speed_rpm
		self.state.torque = max(0.0, torque_from_fuel - load_torque)

		rpm_delta = self.speed_response_coeff * (self.state.torque - load_torque)
		self.state.engine_speed_rpm = max(0.0, self.state.engine_speed_rpm + dt * rpm_delta)

		return self.state

