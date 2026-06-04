from pathlib import Path

from simulation.config_resolver import load_runtime_config, write_resolved_config


def test_load_runtime_config_reads_yaml_defaults():
    runtime_config = load_runtime_config(Path("config"))

    assert runtime_config.project == "engine-control-sim"
    assert runtime_config.simulation["duration_seconds"] == 30.0
    assert runtime_config.simulation["timestep_seconds"] == 0.1
    assert runtime_config.engine["air_inflow_coeff"] == 1.5
    assert runtime_config.controller["type"] == "fixed"
    assert runtime_config.scenario["throttle"] == {-1: 0.6}
    assert runtime_config.scenario["target_air_fuel_ratio"] == {-1: 14.7}


def test_write_resolved_config_emits_yaml(tmp_path):
    runtime_config = load_runtime_config(Path("config"))
    output_path = write_resolved_config(runtime_config, tmp_path / "resolved.yaml")

    assert output_path.exists()
    assert "project: engine-control-sim" in output_path.read_text(encoding="utf-8")