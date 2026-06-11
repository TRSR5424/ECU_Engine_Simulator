from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_settings(config_name: str | None = None):
    if config_name is None:
        return {"settings": "Here are all the current settings!"}
    return {"settings": f"Here are the current {config_name} settings!"}

@router.post("/newExperiment/{experiment_name}")
async def create_new_experiment(experiment_name: str, experiment_settings: dict[str, dict]):
    return {"experiment": experiment_name, "settings": experiment_settings, "message": "Experiment created successfully!"}

@router.post("/update/{experiment_name}")
async def update_settings(experiment_name: str, new_settings: dict[str, dict]):
    return {"experiment": experiment_name, "new_settings": new_settings, "message": "Settings updated successfully!"}

@router.post("/updateGlobal/")
async def update_global_settings(new_settings: dict[str, str]):
    return {"new_settings": new_settings, "message": "Global settings updated successfully!"}

@router.get("/compare/")
async def compare_settings(experiment_name: str):
    return {"compare": True}

@router.post("/setCompare/{value}")
async def set_compare(value: bool):
    return {"compare": value}