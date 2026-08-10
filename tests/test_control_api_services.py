from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import yaml

import control_api._service_utils as service_utils
import control_api.results.results_service as results_service
import control_api.scripts.scripts_service as scripts_service
import control_api.settings.settings_service as settings_service


def _patch_control_roots(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    config_root = tmp_path / "config"
    data_root = tmp_path / "data"

    config_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(service_utils, "CONFIG_ROOT", config_root)
    monkeypatch.setattr(service_utils, "DATA_ROOT", data_root)
    monkeypatch.setattr(settings_service, "CONFIG_ROOT", config_root)
    monkeypatch.setattr(results_service, "DATA_ROOT", data_root)
    monkeypatch.setattr(scripts_service, "DATA_ROOT", data_root)

    return config_root, data_root


def test_settings_service_reads_writes_and_compares_experiments(monkeypatch, tmp_path):
    config_root, _ = _patch_control_roots(monkeypatch, tmp_path)

    base_experiment = config_root / "base"
    demo_experiment = config_root / "demo"
    base_experiment.mkdir(parents=True)
    demo_experiment.mkdir(parents=True)

    (config_root / "global.yaml").write_text(
        yaml.safe_dump({"project": "engine-control-sim", "config_folder": "base", "active_experiment": "base"}),
        encoding="utf-8",
    )
    (base_experiment / "engine.yaml").write_text(yaml.safe_dump({"name": "simple_engine", "torque_coeff": 1.0}), encoding="utf-8")
    (base_experiment / "controller.yaml").write_text(yaml.safe_dump({"type": "fixed"}), encoding="utf-8")
    (base_experiment / "scenario.yaml").write_text(yaml.safe_dump({"throttle": {-1: 0.5}}), encoding="utf-8")
    (base_experiment / "reference.yaml").write_text(yaml.safe_dump({}), encoding="utf-8")
    (base_experiment / "sensor.yaml").write_text(yaml.safe_dump({"type": "identity"}), encoding="utf-8")

    (demo_experiment / "engine.yaml").write_text(yaml.safe_dump({"name": "simple_engine", "torque_coeff": 2.5}), encoding="utf-8")
    (demo_experiment / "controller.yaml").write_text(yaml.safe_dump({"type": "fixed", "gain": 0.2}), encoding="utf-8")
    (demo_experiment / "scenario.yaml").write_text(yaml.safe_dump({"throttle": {-1: 0.7}}), encoding="utf-8")
    (demo_experiment / "reference.yaml").write_text(yaml.safe_dump({}), encoding="utf-8")
    (demo_experiment / "sensor.yaml").write_text(yaml.safe_dump({"type": "actual"}), encoding="utf-8")

    settings = settings_service.get_settings()
    assert settings["active_experiment"] == "base"
    assert settings["experiment_settings"]["engine"]["torque_coeff"] == 1.0

    engine_settings = settings_service.get_settings("engine")
    assert engine_settings["settings"]["name"] == "simple_engine"

    created = settings_service.create_new_experiment(
        "new_experiment",
        {"engine": {"name": "simple_engine"}, "sensor": {"type": "identity"}},
    )
    assert (config_root / "new_experiment" / "engine.yaml").exists()
    assert created["experiment"] == "new_experiment"

    updated = settings_service.update_settings("demo", {"engine": {"torque_coeff": 3.5}})
    assert updated["experiment"] == "demo"
    assert yaml.safe_load((demo_experiment / "engine.yaml").read_text(encoding="utf-8"))["torque_coeff"] == 3.5

    global_update = settings_service.update_global_settings({"logging": {"output_csv": "data/custom/"}})
    assert global_update["settings"]["logging"]["output_csv"] == "data/custom/"

    comparison = settings_service.compare_settings("demo")
    assert comparison["source_experiment"] == "base"
    assert comparison["comparison_experiment"] == "demo"
    assert comparison["has_differences"] is True

    compare_toggle = settings_service.set_compare(True)
    assert compare_toggle["compare"] is True
    assert yaml.safe_load((config_root / "global.yaml").read_text(encoding="utf-8"))["comparison"]["enabled"] is True


def test_results_service_reads_csv_and_graph_artifacts(monkeypatch, tmp_path):
    _, data_root = _patch_control_roots(monkeypatch, tmp_path)

    config_root = tmp_path / "config"
    (config_root / "global.yaml").write_text(
        yaml.safe_dump({"project": "engine-control-sim", "config_folder": "base", "active_experiment": "base"}),
        encoding="utf-8",
    )

    demo_folder = data_root / "demo"
    demo_folder.mkdir(parents=True)
    (demo_folder / "demo_output.csv").write_text(
        "time,engine_speed_rpm,throttle,measured_air_fuel_ratio\n0.0,900.0,0.5,14.7\n0.1,905.0,0.5,14.6\n",
        encoding="utf-8",
    )
    (demo_folder / "analysis_report.txt").write_text("demo report\n", encoding="utf-8")
    (demo_folder / "rpm.png").write_text("fake image", encoding="utf-8")

    summary = results_service.get_results()
    assert summary["active_experiment"] == "base"
    assert summary["results"][0]["experiment"] == "demo"

    csv_results = results_service.get_csv_results("demo")
    assert csv_results["experiment"] == "demo"
    assert csv_results["csv_files"][0]["rows"][0]["engine_speed_rpm"] == "900.0"

    graph_results = results_service.get_graph_results("demo", "rpm")
    assert graph_results["results"][0]["graphs"] == [str(demo_folder / "rpm.png")]


def test_scripts_service_dispatches_simulation_analysis_and_comparison(monkeypatch, tmp_path):
    config_root, data_root = _patch_control_roots(monkeypatch, tmp_path)
    active_experiment = data_root / "demo"
    other_experiment = data_root / "other"
    active_experiment.mkdir(parents=True)
    other_experiment.mkdir(parents=True)

    (config_root / "global.yaml").write_text(
        yaml.safe_dump({"project": "engine-control-sim", "config_folder": "demo", "active_experiment": "demo"}),
        encoding="utf-8",
    )

    runtime_config = SimpleNamespace(
        active_experiment="demo",
        simulation={"duration_seconds": 1.0, "timestep_seconds": 0.1},
        scenario={"throttle": 0.5, "target_air_fuel_ratio": 14.7},
        controller={"type": "fixed"},
        engine={"name": "simple_engine"},
        sensor={"type": "identity"},
        logging={"output_csv": str(data_root)},
    )

    monkeypatch.setattr(scripts_service, "load_runtime_config", lambda: runtime_config)
    monkeypatch.setattr(scripts_service, "write_resolved_config", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(scripts_service, "create_engine", lambda config: {"engine": config})
    monkeypatch.setattr(scripts_service, "create_sensor", lambda config: {"sensor": config})
    monkeypatch.setattr(scripts_service, "ControllerBridge", lambda config: {"controller": config})

    class FakeCsvLogger:
        def __init__(self, run_config):
            self.run_config = run_config

        def write(self, path, records):
            output_path = Path(path) / "demo_output.csv"
            output_path.write_text("time\n0.0\n", encoding="utf-8")
            return output_path

    class FakeSimulator:
        def __init__(self, settings, engine, controller, sensor):
            self.settings = settings
            self.engine = engine
            self.controller = controller
            self.sensor = sensor

        def run(self):
            record = SimpleNamespace(
                time=0.0,
                throttle=0.5,
                fuel_injection=0.1,
                air_mass=1.0,
                fuel_mass=0.2,
                air_fuel_ratio=14.7,
                measured_air_fuel_ratio=14.6,
                engine_speed_rpm=900.0,
                torque=2.0,
            )
            return SimpleNamespace(records=[record])

    monkeypatch.setattr(scripts_service, "CsvLogger", FakeCsvLogger)
    monkeypatch.setattr(scripts_service, "Simulator", FakeSimulator)

    analysis_calls: list[str] = []
    monkeypatch.setattr("analysis.run_analysis.save_single", lambda folder: analysis_calls.append(folder))

    comparison_calls: list[tuple[str, str]] = []
    monkeypatch.setattr("analysis.compare_runs.compare", lambda a_folder, b_folder: comparison_calls.append((a_folder, b_folder)))
    monkeypatch.setattr(scripts_service, "list_experiment_names", lambda: ["demo", "other"])

    simulation_result = scripts_service.run_script("simulation")
    assert simulation_result["status"] == "completed"
    assert simulation_result["records"] == 1
    assert Path(simulation_result["output_csv"]).exists()

    analysis_result = scripts_service.run_script("analysis")
    assert analysis_result["status"] == "completed"
    assert analysis_calls == [str(active_experiment)]

    compare_result = scripts_service.run_script("compare_runs")
    assert compare_result["status"] == "completed"
    assert comparison_calls == [(str(active_experiment), str(other_experiment))]

    all_result = scripts_service.run_all_scripts()
    assert [item["script"] for item in all_result["scripts"]] == ["simulation", "analysis", "compare_runs"]
