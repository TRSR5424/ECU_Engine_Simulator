from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

import settings_service as service

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_settings(config_name: str | None = None):
    results = service.get_settings(config_name)
    return results

@router.post("/newExperiment/{experiment_name}")
async def create_new_experiment(experiment_name: str, experiment_settings: dict[str, dict]):
    results = service.create_new_experiment(experiment_name, experiment_settings)
    return results

@router.post("/update/{experiment_name}")
async def update_settings(experiment_name: str, new_settings: dict[str, dict]):
    results = service.update_settings(experiment_name, new_settings)
    return results

@router.post("/updateGlobal/")
async def update_global_settings(new_settings: dict[str, str]):
    results = service.update_global_settings(new_settings)
    return results

@router.get("/compare/")
async def compare_settings(experiment_name: str):
    results = service.compare_settings(experiment_name)
    return results

@router.post("/setCompare/{value}")
async def set_compare(value: bool):
    results = service.set_compare(value)
    return results