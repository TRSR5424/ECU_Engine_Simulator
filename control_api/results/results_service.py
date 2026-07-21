from __future__ import annotations

from pathlib import Path
from typing import Any

from control_api._service_utils import DATA_ROOT, list_matching_files, load_global_config, read_csv_preview


def _experiment_folder(experiment_name: str) -> Path:
    folder = DATA_ROOT / experiment_name
    if not folder.exists():
        raise FileNotFoundError(f"Unknown experiment '{experiment_name}'")
    return folder


def _result_summary(folder: Path) -> dict[str, Any]:
    csv_files = list_matching_files(folder, [".csv"])
    info_files = list_matching_files(folder, [".txt"])
    graph_files = list_matching_files(folder, [".png"])
    return {
        "experiment": folder.name,
        "path": str(folder),
        "csv_files": [str(path) for path in csv_files],
        "info_files": [str(path) for path in info_files],
        "graph_files": [str(path) for path in graph_files],
    }


def get_results() -> dict[str, Any]:
    runtime_config = load_global_config()
    active_experiment = runtime_config.get("active_experiment", "default")
    if not DATA_ROOT.exists():
        return {"active_experiment": active_experiment, "results": []}

    experiments = [entry for entry in sorted(DATA_ROOT.iterdir()) if entry.is_dir() and not entry.name.startswith(".")]
    return {
        "active_experiment": active_experiment,
        "results": [_result_summary(folder) for folder in experiments],
    }


def get_experiment_results(experiment_name: str | None = None) -> dict[str, Any]:
    if experiment_name is None:
        return get_results()

    folder = _experiment_folder(experiment_name)
    return {
        "experiment": experiment_name,
        "summary": _result_summary(folder),
    }


def get_csv_results(experiment_name: str | None = None) -> dict[str, Any]:
    if experiment_name is None:
        return {
            "results": [
                {
                    "experiment": folder.name,
                    "csv": read_csv_preview(csv_file),
                }
                for folder in sorted(DATA_ROOT.iterdir())
                if folder.is_dir() and not folder.name.startswith(".")
                for csv_file in list_matching_files(folder, [".csv"])
            ]
            if DATA_ROOT.exists()
            else []
        }

    folder = _experiment_folder(experiment_name)
    csv_files = list_matching_files(folder, [".csv"])
    return {
        "experiment": experiment_name,
        "csv_files": [read_csv_preview(csv_file) for csv_file in csv_files],
    }


def get_graph_results(experiment_name: str | None = None, graph_type: str | None = None) -> dict[str, Any]:
    if experiment_name is None:
        folders = [entry for entry in sorted(DATA_ROOT.iterdir()) if entry.is_dir() and not entry.name.startswith(".")]
    else:
        folders = [_experiment_folder(experiment_name)]

    selected_graph_type = graph_type.lower().strip() if graph_type else None
    results = []

    for folder in folders:
        graph_files = list_matching_files(folder, [".png"])
        if selected_graph_type is not None:
            graph_files = [path for path in graph_files if selected_graph_type in path.name.lower()]

        results.append(
            {
                "experiment": folder.name,
                "graphs": [str(path) for path in graph_files],
            }
        )

    return {
        "experiment": experiment_name or "all",
        "graph_type": graph_type,
        "results": results,
    }

