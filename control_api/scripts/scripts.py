from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

import control_api.scripts.scripts_service as service

router = APIRouter(
    prefix="/scripts",
    tags=["scripts"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_scripts():
    scripts = service.get_scripts()
    return scripts

@router.get("/run/{script_name}")
async def run_script(script_name: str):
    results = service.run_script(script_name)
    return results

@router.get("/runall/")
async def run_all_scripts():
    results = service.run_all_scripts()
    return results