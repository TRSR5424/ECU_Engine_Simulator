from engine.simple_engine import SimpleEngine
from simulation.simulator import Simulator, SimulationSettings


def test_simple_engine_advances_state():
    engine = SimpleEngine()

    initial_speed = engine.state.engine_speed_rpm
    state = engine.step(throttle=0.5, fuel_injection=0.1, dt=0.1)

    assert state.engine_speed_rpm >= 0.0
    assert state.engine_speed_rpm != initial_speed
    assert state.torque >= 0.0


def test_simulator_runs_fixed_variable_loop():
    simulator = Simulator(
        settings=SimulationSettings(duration=0.5, dt=0.1, throttle=0.5, fuel_injection=0.1)
    )

    result = simulator.run()

    assert len(result.records) == 5
    assert result.records[0].throttle == 0.5
    assert result.records[-1].time == 0.4
