engine-control-sim
===================

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

Reference-data evaluation
-------------------------

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

Local run
---------

Run the simulator directly from the repository root:

```bash
python simulation/main.py
```

This project is a standalone engine-control simulator and no longer includes the separate Docker, website, or control API stack.

c++ build
cmake -B build -DCMAKE_BUILD_TYPE=Release   
cmake --build build --config Release                   