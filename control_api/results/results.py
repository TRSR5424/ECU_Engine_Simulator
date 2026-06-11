from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

import results_service as service

router = APIRouter(
    prefix="/results",
    tags=["results"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_results():
    results = service.get_results()
    return results

@router.get("/experiments/")
async def get_experiment_results(experiment_name: str | None = None):
    results = service.get_experiment_results(experiment_name)
    return results

@router.get("/csv/")
async def get_csv_results(experiment_name: str | None = None):
    results = service.get_csv_results(experiment_name)
    return results

@router.get("/graph/")
async def get_graph_results(experiment_name: str | None = None, graph_type: str | None = None):
    results = service.get_graph_results(experiment_name, graph_type)
    return results