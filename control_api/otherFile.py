from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

router = APIRouter(
    prefix="/other",
    tags=["other"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/secure-info/")
async def secure_info():
    return {"info": "This is some secure information!"}
