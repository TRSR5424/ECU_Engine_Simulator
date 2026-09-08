from engine.engine_base import EngineBase, EngineState
from engine.engine_factory import create_engine
from controller.bindings.controller_bridge import ControllerBridge
from sensor.sensor_base import SensorBase
from simulation.simulator import Simulator, SimulationSettings


class RecordingController(ControllerBridge):
    def __init__(self):
        self._lib = None
        self._handle = None
        self._controller_type = "fixed"
        self.inputs = []

    def compute(self, input):
        self.inputs.append(input)
        return 0.08


class RecordingEngine(EngineBase):
    def __init__(self):
        self.state = EngineState()

    def step(self, throttle: float, fuel_injection: float, dt: float) -> EngineState:
        self.state = EngineState(
            air_mass=self.state.air_mass + throttle,
            fuel_mass=self.state.fuel_mass + fuel_injection,
            engine_speed_rpm=self.state.engine_speed_rpm + throttle * 10.0,
            torque=self.state.torque + fuel_injection,
        )
        return self.state


class IdentitySensor(SensorBase):
    def read(self, actual_state: float) -> float:
        return actual_state


def test_simple_engine_advances_state():
    engine = create_engine()
    initial_speed = engine.state.engine_speed_rpm
    initial_air = engine.state.air_mass
    initial_fuel = engine.state.fuel_mass
    state = engine.step(throttle=0.5, fuel_injection=0.1, dt=0.1)

    assert state.engine_speed_rpm >= 0.0
    # torque may be negative (engine braking) depending on parameters
    assert isinstance(state.torque, float)
    # ensure the engine state advanced in at least one field (rpm, air_mass, or fuel_mass)
    assert (
        state.engine_speed_rpm != initial_speed
        or state.air_mass != initial_air
        or state.fuel_mass != initial_fuel
    )


def test_simulator_runs_fixed_variable_loop():
    simulator = Simulator(
        settings=SimulationSettings(duration=0.5, dt=0.1, throttle=0.5)
    )

    result = simulator.run()

    assert len(result.records) == 6
    assert result.records[0].fuel_injection == 0.08
    assert result.records[0].throttle == 0.5
    assert result.records[-1].time == 0.4


def test_simulator_uses_step_scheduled_throttle_and_target_afr():
    engine = RecordingEngine()
    controller = RecordingController()
    sensor = IdentitySensor()

    simulator = Simulator(
        settings=SimulationSettings(
            duration=1.2,
            dt=0.1,
            throttle={-1: 0.2, 0: 0.2, 3: 0.4},
            target_air_fuel_ratio={-1: 14.7, 0: 14.7, 10: 13.2},
        ),
        engine=engine,
        controller=controller,
        sensor=sensor,
    )

    result = simulator.run()

    assert result.records[0].throttle == 0.2
    assert result.records[3].throttle == 0.2
    assert result.records[4].throttle == 0.4
    assert result.records[10].throttle == 0.4

    assert controller.inputs[0].target_air_fuel_ratio == 14.7
    assert controller.inputs[10].target_air_fuel_ratio == 14.7
    assert controller.inputs[11].target_air_fuel_ratio == 13.2


def test_simulator_rejects_time_based_schedule_without_step_zero():
    simulator = Simulator(
        settings=SimulationSettings(
            duration=0.2,
            dt=0.1,
            throttle={-1: 0.2, 3: 0.4},
            target_air_fuel_ratio={-1: 14.7, 10: 13.2},
        ),
        engine=RecordingEngine(),
        controller=RecordingController(),
        sensor=IdentitySensor(),
    )

    try:
        simulator.run()
    except ValueError as exc:
        assert "step 0" in str(exc)
    else:
        raise AssertionError("Expected a ValueError for schedules missing step 0")
