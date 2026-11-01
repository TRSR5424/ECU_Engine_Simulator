# ECU Engine Simulator

The ECU Engine Simulator is a configurable, timestep-based engine-control
simulation. It combines a Python simulation shell with a native C++ controller
library exposed through `ctypes`. The project is intended for repeatable
controller experiments, sensor-behavior experiments, and comparison against
external reference datasets.

## Architecture

Each simulation step follows the same data flow:

1. The input schedule resolves throttle, target AFR, and load torque.
2. Configured sensors measure the previous engine state.
3. The controller receives those measurements and computes fuel injection.
4. The engine advances by one timestep.
5. Invariants validate the controller output and resulting engine state.
6. The logger records the state and inputs for later analysis.

The main Python packages are:

- [`engine/`](engine/) - engine state, dynamics, factories, and physics helpers.
- [`sensor/`](sensor/) - ideal, noisy, delayed, and AFR-specific sensors.
- [`simulation/`](simulation/) - configuration, orchestration, validation, and logging.
- [`reference_model/`](reference_model/) - optional expected-value models.
- [`analysis/`](analysis/) - plots and comparisons for experiment output.
- [`controller/`](controller/) - C++ controller implementations and the Python bridge.

## Quick start

### Prerequisites

- Python 3.11+ (recommended)
- A C++17 compiler and CMake 3.10+ for the native controller library
- `pip` available

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Build the native controller library:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

Run the test suite:

```bash
python -m pytest -q
```

Run a single simulation:

```bash
python simulation/main.py
```

## Configuration and experiments

The active configuration folder is selected in
[config/global.yaml](config/global.yaml) with the `config_folder` key. The
selected folder can override the base engine, controller, scenario, reference,
and sensor YAML files.

1. Copy the relevant files into a new folder under `config/`, for example
   `config/my_experiment/`.
2. Set `config_folder: my_experiment` in [config/global.yaml](config/global.yaml).
3. Run the simulator. The resolver merges the selected overrides with the base
   configuration and writes the resolved configuration to
   `config/active/resolved_config.yaml`.

The active configuration controls the engine model, controller selection,
sensor chain, reference model, simulation duration, timestep, input schedules,
and output location. Use [config/global.yaml.example](config/global.yaml.example)
as a starting point for a new checkout.

## Controllers and sensors

The controller bridge passes the current simulation context to the native
library, including throttle, target AFR, engine speed, torque, air mass, fuel
mass, and named sensor measurements. The available controller metadata includes
fixed-output, PID, mapped-PID, and true-mapped variants. The CMake target
currently builds the fixed and PID controller sources used by the default
binding; additional controller sources are available under
[controller/src/](controller/src/) for future configurations.

Sensors are composable. The identity sensor exposes the current value, while
the noisy and delayed sensors model measurement imperfections. AFR-specific
wrappers expose these behaviors through the `air_fuel_ratio` signal expected by
the feedback controllers.

## Simulation output

CSV output contains the timestep, throttle, load torque, fuel injection, air
and fuel mass, actual and measured AFR, target AFR, engine speed, and torque.
Run metadata records the resolved configuration and source revision when
available. Output folders under `data/` can therefore be regenerated and
analysed independently.

## Analysis

The analysis scripts operate on an experiment output folder containing a CSV
file. They select the first CSV, generate plots, and write the results back
into the same directory.

Analyse one experiment:

```bash
python analysis/run_analysis.py data/default
```

Compare two experiments:

```bash
python analysis/run_analysis.py data/default --other data/first_experiment
```

This creates plots such as `afr_plot.png`, `rpm_plot.png`,
`throttle_plot.png`, and additional diagnostics in the experiment folder. When
you compare two folders, matching `_Comparison` folders are created in both
locations with comparison plots for AFR, RPM, and throttle.

## Reference-data evaluation

`analysis/compare_with_reference_datasets.py` compares a simulator CSV with local
copies of the [VED](https://github.com/gsoh/VED) dynamic data and/or
[EngineFaultDB](https://github.com/leoxthomas/EngineFaultDB) data. The script does
not download or modify upstream data, so the exact files used for a dissertation
remain reproducible. It writes numeric results to `metrics.csv` and `metrics.json`,
and a plain-language interpretation to `report.md`.

```bash
python analysis/compare_with_reference_datasets.py ^
  --simulator data/default ^
  --ved path/to/VED_DynamicData.csv ^
  --enginefaultdb path/to/EngineFaultDB.csv ^
  --output analysis/results/reference_comparison
```

Either reference argument may be omitted. For a quick run on a large VED file,
add `--max-reference-rows 100000`. The report explicitly records the matched
columns, units, standardized mean differences, and limitations: VED is
naturalistic vehicle data and EngineFaultDB is controlled fault data, so these
comparisons are descriptive evidence rather than direct same-engine validation.

The supplied EngineFaultDB file is available at
`analysis/outside_data/EngineFaultDB_Final.csv`, so it is used automatically:

```bash
python analysis/compare_with_reference_datasets.py ^
  --simulator data/default ^
  --output analysis/results/enginefaultdb_comparison
```

The supplied VED files are `.7z` archives. Extract both archives with 7-Zip
into `analysis/outside_data`; the script automatically aggregates all extracted
`VED_*_week.csv` files when `--ved` is omitted. For a quicker evaluation, add
`--max-reference-rows 10000`, which reads at most 10,000 rows from each VED
weekly file. EngineFaultDB is always read in full.

## Repository layout and development notes

Run commands from the repository root so Python package imports and relative
configuration paths resolve correctly:

```bash
python simulation/main.py
```

This project is a standalone engine-control simulator. It does not include the
separate Docker, website, or control API stack from earlier prototypes.