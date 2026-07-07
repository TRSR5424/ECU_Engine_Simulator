from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Request

from website_api.client import forward_to_control_api, get_control_api_base_url


router = APIRouter(prefix="/api", tags=["website-api"])


@router.get("/health")
async def website_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "control_api_base_url": get_control_api_base_url(),
    }


@router.get("/control")
async def control_overview() -> dict[str, Any]:
    return {
        "service": "website-api",
        "control_api_base_url": get_control_api_base_url(),
        "routes": [
            "/api/control/health",
            "/api/control/version",
            "/api/control/status",
            "/api/control/echo/path/{message}",
            "/api/control/echo/query",
            "/api/control/secure-data",
            "/api/control/settings",
            "/api/control/settings/newExperiment/{experiment_name}",
            "/api/control/settings/update/{experiment_name}",
            "/api/control/settings/updateGlobal",
            "/api/control/settings/compare",
            "/api/control/settings/setCompare/{value}",
            "/api/control/scripts",
            "/api/control/scripts/run/{script_name}",
            "/api/control/scripts/runall",
            "/api/control/results",
            "/api/control/results/experiments",
            "/api/control/results/csv",
            "/api/control/results/graph",
            "/api/control/other/secure-info",
        ],
    }


@router.get("/control/health")
async def proxy_control_health() -> Any:
    return await forward_to_control_api("GET", "/health")


@router.get("/control/version")
async def proxy_control_version() -> Any:
    return await forward_to_control_api("GET", "/version")


@router.get("/control/status")
async def proxy_control_status() -> Any:
    return await forward_to_control_api("GET", "/status")


@router.get("/control/echo/path/{message}")
async def proxy_control_echo_path(message: str) -> Any:
    return await forward_to_control_api("GET", f"/echo/path/{message}")


@router.get("/control/echo/query")
async def proxy_control_echo_query(message: str = "No message provided") -> Any:
    return await forward_to_control_api("GET", "/echo/query/", params={"message": message})


@router.get("/control/secure-data")
async def proxy_control_secure_data() -> Any:
    return await forward_to_control_api("GET", "/secure-data/")


@router.get("/control/settings")
async def proxy_control_settings(config_name: str | None = None) -> Any:
    params = {} if config_name is None else {"config_name": config_name}
    return await forward_to_control_api("GET", "/settings/", params=params)


@router.post("/control/settings/newExperiment/{experiment_name}")
async def proxy_control_settings_new_experiment(
    experiment_name: str,
    experiment_settings: dict[str, Any] = Body(default_factory=dict),
) -> Any:
    return await forward_to_control_api(
        "POST",
        f"/settings/newExperiment/{experiment_name}",
        json_body=experiment_settings,
    )


@router.post("/control/settings/update/{experiment_name}")
async def proxy_control_settings_update(
    experiment_name: str,
    new_settings: dict[str, Any] = Body(default_factory=dict),
) -> Any:
    return await forward_to_control_api(
        "POST",
        f"/settings/update/{experiment_name}",
        json_body=new_settings,
    )


@router.post("/control/settings/updateGlobal")
async def proxy_control_settings_update_global(
    new_settings: dict[str, Any] = Body(default_factory=dict),
) -> Any:
    return await forward_to_control_api("POST", "/settings/updateGlobal/", json_body=new_settings)


@router.get("/control/settings/compare")
async def proxy_control_settings_compare(experiment_name: str) -> Any:
    return await forward_to_control_api("GET", "/settings/compare/", params={"experiment_name": experiment_name})


@router.post("/control/settings/setCompare/{value}")
async def proxy_control_settings_set_compare(value: bool) -> Any:
    return await forward_to_control_api("POST", f"/settings/setCompare/{str(value).lower()}")


@router.get("/control/scripts")
async def proxy_control_scripts() -> Any:
    return await forward_to_control_api("GET", "/scripts/")


@router.get("/control/scripts/run/{script_name}")
async def proxy_control_scripts_run(script_name: str) -> Any:
    return await forward_to_control_api("GET", f"/scripts/run/{script_name}")


@router.get("/control/scripts/runall")
async def proxy_control_scripts_run_all() -> Any:
    return await forward_to_control_api("GET", "/scripts/runall/")


@router.get("/control/results")
async def proxy_control_results() -> Any:
    return await forward_to_control_api("GET", "/results/")


@router.get("/control/results/experiments")
async def proxy_control_results_experiments(experiment_name: str | None = None) -> Any:
    params = {} if experiment_name is None else {"experiment_name": experiment_name}
    return await forward_to_control_api("GET", "/results/experiments/", params=params)


@router.get("/control/results/csv")
async def proxy_control_results_csv(experiment_name: str | None = None) -> Any:
    params = {} if experiment_name is None else {"experiment_name": experiment_name}
    return await forward_to_control_api("GET", "/results/csv/", params=params)


@router.get("/control/results/graph")
async def proxy_control_results_graph(
    experiment_name: str | None = None,
    graph_type: str | None = None,
) -> Any:
    params: dict[str, Any] = {}
    if experiment_name is not None:
        params["experiment_name"] = experiment_name
    if graph_type is not None:
        params["graph_type"] = graph_type
    return await forward_to_control_api("GET", "/results/graph/", params=params)


@router.get("/control/other/secure-info")
async def proxy_control_other_secure_info() -> Any:
    return await forward_to_control_api("GET", "/other/secure-info/")