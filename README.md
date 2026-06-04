engine-control-sim
===================

Repository skeleton for the engine control simulator project.

Structure
---------

engine-control-sim/
├── README.md
├── requirements.txt
├── CMakeLists.txt
├── .gitignore
├── config/
├── simulation/
├── engine/
├── controller/
├── reference_model/
├── sensor/
├── analysis/
├── ui/
├── data/
├── tests/
└── build/

See the `FileStructure` file for a more detailed tree.

Quick Start
-----------

Prerequisites:

- Python 3.11+ (recommended)
- `pip` available

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest -q
```

Run a single simulation:

```bash
python simulation/main.py
```

Configuration and experiments
-----------------------------

The active configuration folder is set in [config/global.yaml](config/global.yaml#L1-L20) via the `config_folder` key. To run an experiment:

1. Create a new folder under `config/`, e.g. `config/my_experiment`, containing any of the YAML files you wish to override (`engine.yaml`, `controller.yaml`, `scenario.yaml`, `reference.yaml`, `sensor.yaml`).
2. Update `config/global.yaml` and set `config_folder: my_experiment`.
3. Run the simulator as above — the resolver will load YAMLs from the selected folder and write a resolved copy to `config/active/resolved_config.yaml` when invoked.

Analysis
--------

The analysis scripts work on an experiment output folder that contains a CSV file. They automatically pick the first CSV in the folder, generate plots, and write the results back into the same directory.

Run analysis for one experiment:

```bash
python analysis/run_analysis.py data/default
```

Compare two experiments:

```bash
python analysis/run_analysis.py data/default --other data/first_experiment
```

This creates plots such as `afr.png`, `rpm.png`, `throttle.png`, and additional diagnostics in the experiment folder. When you compare two folders, matching `_Comparison` folders are created in both locations with comparison plots for AFR, RPM, and throttle.

c++ build
cmake -B build -DCMAKE_BUILD_TYPE=Release   
cmake --build build --config Release                   