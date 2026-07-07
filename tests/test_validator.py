from controller.bindings.controller_bridge import ControllerBridge
from engine.engine_factory import create_engine
from sensor.sensor_factory import create_sensor
from simulation.validator import ConfigurationValidationError
from simulation.validator import validate


def test_validate_accepts_current_default_configuration():
    engine = create_engine()
    sensor = create_sensor()
    controller = ControllerBridge(config={"type": "fixed"})

    validate(engine, sensor, controller)


def test_validate_rejects_missing_required_sensor():
    engine = create_engine()
    controller = ControllerBridge(config={"type": "fixed"})

    try:
        validate(engine, [], controller)
    except ConfigurationValidationError as exc:
        assert "Missing" in str(exc)
        assert "oxygen_sensor" in str(exc)
    else:
        raise AssertionError("Expected configuration validation to fail")


def test_validate_rejects_missing_required_signal():
    class SensorWithoutAfr:
        sensor_type = "oxygen_sensor"
        provided_signals = frozenset({"rpm"})

        def read(self, actual_state: float) -> float:
            return actual_state

    engine = create_engine()
    controller = ControllerBridge(config={"type": "fixed"})

    try:
        validate(engine, SensorWithoutAfr(), controller)
    except ConfigurationValidationError as exc:
        assert "Missing" in str(exc)
        assert "air_fuel_ratio" in str(exc)
    else:
        raise AssertionError("Expected configuration validation to fail")