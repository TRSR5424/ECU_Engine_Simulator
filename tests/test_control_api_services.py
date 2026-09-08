
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
