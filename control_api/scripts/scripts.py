from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

router = APIRouter(
    prefix="/scripts",
    tags=["scripts"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_scripts():
    return {"scripts": "Here are the available scripts!"}

@router.get("/run/{script_name}")
async def run_script(script_name: str):
    return {"script": script_name, "details": "Here are the details for the script!"}

@router.get("/runall/")
async def run_all_scripts():
    return {"scripts": "All scripts have been run!"}