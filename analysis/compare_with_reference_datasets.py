"""Compare simulator output with VED and EngineFaultDB observations.

The reference files are intentionally supplied by the user.  This avoids
silently changing the evaluation set when an upstream repository is updated.

Examples (from the repository root):

    python analysis/compare_with_reference_datasets.py ^
        --simulator data/default ^
        --ved path/to/VED_DynamicData.csv ^
        --enginefaultdb path/to/EngineFaultDB.csv ^
        --output analysis/results/reference_comparison

The command writes ``metrics.csv``, ``metrics.json`` and ``report.md``.
Reference columns are matched case-insensitively and punctuation-insensitively.
Use ``--max-reference-rows`` for a quick development run on large VED files.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ALIASES: dict[str, tuple[str, ...]] = {
    "rpm": (
        "engine_speed_rpm",
        "rpm",
        "engine_rpm",
        "engine_speed",
        "engine_rpm_rpm",
    ),
    "afr": ("air_fuel_ratio", "afr", "air_fuel_equivalence_ratio"),
    "throttle": ("throttle", "tps", "throttle_position", "throttle_position_sensor"),
    "torque": ("torque", "force", "engine_torque"),
    "power": ("power", "engine_power"),
    "speed": ("speed", "vehicle_speed", "vehicle_speed_kmh"),
    "fuel_rate": (
        "fuel_rate",
        "fuel_rate_l_hr",
        "fuel_rate_l_h",
        "fuel_consumption_l_h",
        "fuel_consumption_l_hr",
        "fuel_consumption_lh",
        "consumption_l_h",
        "consumption_l_hr",
        "consumption_lh",
    ),
    "maf": ("maf", "mass_air_flow", "mass_air_flow_g_sec", "maf_g_sec"),
    "lambda": ("lambda", "lambda_value"),
}

REFERENCE_URLS = {
    "VED": "https://github.com/gsoh/VED",
    "EngineFaultDB": "https://github.com/leoxthomas/EngineFaultDB",
}

UNITS = {
    "rpm": "RPM",
    "afr": "dimensionless air/fuel mass ratio",
    "throttle": "percent (reference) or model fraction (simulator)",
    "torque": "dataset-defined (force may be N; simulator torque is model units)",
    "power": "kW",
    "speed": "km/h",
    "fuel_rate": "L/h",
    "maf": "g/s",
    "lambda": "dimensionless",
}


def _normalise(name: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def _find_csv(path: Path) -> Path:
    if path.is_file():
        if path.suffix.lower() == ".7z":
            raise ValueError(
                f"{path.name} is a VED archive. Extract it first with 7-Zip, "
                "then pass the extracted dynamic-data CSV to --ved."
            )
        return path
    files = sorted(list(path.rglob("*.csv")) + list(path.rglob("*.xls")) + list(path.rglob("*.xlsx")))
    if not files:
        raise FileNotFoundError(f"No CSV file found below {path}")
    if len(files) > 1:
        # Multiple files are valid for VED, which is distributed as weekly CSVs.
        # The reader concatenates them while retaining one consistent schema.
        preferred = [f for f in files if "output" in f.name.lower()]
        if len(preferred) == 1:
            return preferred[0]
        raise ValueError(f"Multiple CSV files found below {path}; pass one CSV or use a VED directory")
    return files[0]


def _read_dataset(path: Path, max_rows: int | None) -> pd.DataFrame:
    if path.is_dir():
        files = sorted(path.rglob("VED_*.csv"))
        if not files:
            files = sorted(path.rglob("*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV file found below {path}")
        frames = [pd.read_csv(file, nrows=max_rows, low_memory=False) for file in files]
        return pd.concat(frames, ignore_index=True)
    path = _find_csv(path)
    if path.suffix.lower() in {".xls", ".xlsx"}:
        return pd.read_excel(path, nrows=max_rows)
    return pd.read_csv(path, nrows=max_rows, low_memory=False)


def _column_map(frame: pd.DataFrame) -> dict[str, str]:
    normalised = {_normalise(column): str(column) for column in frame.columns}
    result: dict[str, str] = {}
    for metric, aliases in ALIASES.items():
        for alias in aliases:
            if _normalise(alias) in normalised:
                result[metric] = normalised[_normalise(alias)]
                break
    return result


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()


def _summary(values: pd.Series) -> dict[str, float | int]:
    if values.empty:
        return {"n": 0}
    quantiles = values.quantile([0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "n": int(values.size),
        "mean": float(values.mean()),
        "std": float(values.std(ddof=1)) if values.size > 1 else 0.0,
        "min": float(values.min()),
        "p05": float(quantiles.loc[0.05]),
        "median": float(quantiles.loc[0.5]),
        "p75": float(quantiles.loc[0.75]),
        "p95": float(quantiles.loc[0.95]),
        "max": float(values.max()),
    }


def _metric_row(
    metric: str,
    simulator: pd.Series,
    reference: pd.Series,
    dataset: str,
    reference_column: str,
) -> dict[str, Any]:
    sim = _summary(simulator)
    ref = _summary(reference)
    sim_mean = float(sim.get("mean", np.nan))
    ref_mean = float(ref.get("mean", np.nan))
    pooled = np.sqrt((float(sim.get("std", 0.0)) ** 2 + float(ref.get("std", 0.0)) ** 2) / 2)
    return {
        "dataset": dataset,
        "metric": metric,
        "unit": UNITS[metric],
        "simulator_column": metric,
        "reference_column": reference_column,
        "simulator_n": sim.get("n", 0),
        "reference_n": ref.get("n", 0),
        "simulator_mean": sim_mean,
        "reference_mean": ref_mean,
        "mean_difference": sim_mean - ref_mean,
        "mean_ratio_simulator_to_reference": sim_mean / ref_mean if ref_mean else np.nan,
        "pooled_sd": pooled,
        "standardized_mean_difference": (sim_mean - ref_mean) / pooled if pooled else 0.0,
        "simulator_median": sim.get("median", np.nan),
        "reference_median": ref.get("median", np.nan),
        "simulator_p05": sim.get("p05", np.nan),
        "simulator_p95": sim.get("p95", np.nan),
        "reference_p05": ref.get("p05", np.nan),
        "reference_p95": ref.get("p95", np.nan),
    }


def _interpret(row: dict[str, Any]) -> str:
    simulator = float(row["simulator_mean"])
    reference = float(row["reference_mean"])
    difference = simulator - reference
    direction = "higher" if difference > 0 else "lower" if difference < 0 else "the same as"
    meanings = {
        "rpm": "engine operating speed",
        "afr": "air-fuel mixture; a higher value indicates a leaner mixture",
        "throttle": "throttle demand; the simulator and reference scales may differ",
        "torque": "engine output force; zero indicates that the simulator is not producing model torque",
        "fuel_rate": "fuel used per hour",
        "maf": "air entering the engine per second",
        "lambda": "combustion mixture relative to stoichiometric air-fuel ratio",
        "power": "engine power output",
        "speed": "vehicle speed",
    }
    return (
        f"The simulator mean is {direction} than the reference. "
        f"This might indicate a different operating range or calibration for "
        f"{meanings.get(row['metric'], row['metric'])}."
    )


def _fault_summary(frame: pd.DataFrame, columns: dict[str, str]) -> list[dict[str, Any]]:
    aliases = ("fault", "fault_type", "label", "class", "target")
    normalised = {_normalise(column): str(column) for column in frame.columns}
    label_column = next((normalised[_normalise(alias)] for alias in aliases if _normalise(alias) in normalised), None)
    if label_column is None:
        return []
    rows: list[dict[str, Any]] = []
    for label, group in frame.groupby(label_column, dropna=True):
        for metric, column in columns.items():
            values = _numeric(group, column)
            summary = _summary(values)
            if summary["n"]:
                rows.append({"fault_label": str(label), "metric": metric, **summary})
    return rows


def _markdown_report(
    rows: list[dict[str, Any]],
    fault_rows: list[dict[str, Any]],
    datasets: dict[str, dict[str, Any]],
) -> str:
    lines = [
        "# Reference-data numbers",
        "",
        "## Data counts",
        "",
        "| Dataset | Rows |",
        "|---|---:|",
    ]
    for name, info in datasets.items():
        lines.append(f"| {name} | {info['rows_read']} |")
    lines += [
        "",
        "## Simulator and reference means",
        "",
        "| Dataset | Measurement | Unit | Simulator mean | Reference mean | Difference |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['metric']} | {row['unit']} | "
            f"{row['simulator_mean']:.6g} | {row['reference_mean']:.6g} | "
            f"{row['mean_difference']:.6g} |"
        )
        lines.append(f"| Meaning | {_interpret(row)} | | | | |")
    if not rows:
        lines.append("| No compatible numeric columns were found. | | | | | |")
    if fault_rows:
        lines += [
            "",
            "## EngineFaultDB numbers by fault label",
            "",
            "| Fault | Measurement | Rows | Mean | Median | Standard deviation |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for row in fault_rows:
            lines.append(
                f"| {row['fault_label']} | {row['metric']} | {row['n']} | "
                f"{row['mean']:.6g} | {row['median']:.6g} | {row['std']:.6g} |"
            )
    return "\n".join(lines) + "\n"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def compare(
    simulator_path: Path,
    ved_path: Path | None,
    fault_path: Path | None,
    output_path: Path,
    max_reference_rows: int | None = None,
) -> dict[str, Any]:
    simulator_frame = _read_dataset(simulator_path, None)
    simulator_columns = _column_map(simulator_frame)
    rows: list[dict[str, Any]] = []
    datasets: dict[str, dict[str, Any]] = {
        "simulator": {
            "rows_read": int(len(simulator_frame)),
            "matched_columns": sorted(simulator_columns),
            "source": str(simulator_path),
        }
    }
    simulator_values = {metric: _numeric(simulator_frame, column) for metric, column in simulator_columns.items()}

    fault_rows: list[dict[str, Any]] = []
    for name, path in (("VED", ved_path), ("EngineFaultDB", fault_path)):
        if path is None:
            continue
        row_limit = max_reference_rows if name == "VED" else None
        frame = _read_dataset(path, row_limit)
        columns = _column_map(frame)
        datasets[name] = {
            "rows_read": int(len(frame)),
            "matched_columns": sorted(columns),
            "source": str(path),
            "reference_url": REFERENCE_URLS[name],
        }
        for metric, column in columns.items():
            if metric in simulator_values:
                rows.append(_metric_row(metric, simulator_values[metric], _numeric(frame, column), name, column))
        if name == "EngineFaultDB":
            fault_rows = _fault_summary(frame, columns)

    output_path.mkdir(parents=True, exist_ok=True)
    report = {
        "method": {
            "standardized_mean_difference": "difference in means divided by pooled standard deviation",
            "interpretation": "absolute effect sizes below 0.2, 0.5, and 0.8 are descriptive small, moderate, and large thresholds",
            "warning": "comparisons are distributional and are not same-vehicle validation",
        },
        "datasets": datasets,
        "metrics": rows,
        "enginefaultdb_by_fault": fault_rows,
    }
    (output_path / "metrics.json").write_text(
        json.dumps(_json_safe(report), indent=2, allow_nan=False, default=str),
        encoding="utf-8",
    )
    pd.DataFrame(rows).to_csv(output_path / "metrics.csv", index=False)
    (output_path / "report.md").write_text(_markdown_report(rows, fault_rows, datasets), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulator", required=True, type=Path, help="Simulator CSV or folder containing one CSV")
    parser.add_argument(
        "--ved",
        type=Path,
        default=Path("analysis/outside_data"),
        help="Extracted VED CSV or directory of VED weekly CSVs (default: analysis/outside_data)",
    )
    parser.add_argument(
        "--enginefaultdb",
        type=Path,
        default=Path("analysis/outside_data/EngineFaultDB_Final.csv"),
        help="Local EngineFaultDB CSV (default: analysis/outside_data/EngineFaultDB_Final.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/results/reference_comparison"),
        help="Output directory (default: analysis/results/reference_comparison)",
    )
    parser.add_argument(
        "--max-reference-rows",
        type=int,
        help="Read at most this many rows per VED weekly file; EngineFaultDB is read in full",
    )
    args = parser.parse_args()
    report = compare(args.simulator, args.ved, args.enginefaultdb, args.output, args.max_reference_rows)
    print(f"Wrote {len(report['metrics'])} metric comparisons to {args.output}")
    print(f"Report: {args.output / 'report.md'}")


if __name__ == "__main__":
    main()
