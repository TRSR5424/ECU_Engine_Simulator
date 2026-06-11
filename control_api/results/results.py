from fastapi import APIRouter, Depends

from control_api.dependencies import verify_api_key

router = APIRouter(
    prefix="/results",
    tags=["results"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_results():
    return {"results": "Here are the results!"}

@router.get("/experiments/")
async def get_experiment_results(experiment_name: str | None = None):
    if experiment_name is None:
        return {"experiment": "all", "results": "Here are the results for all experiments!"}
    return {"experiment": experiment_name, "results": "Here are the results for the experiment!"}

@router.get("/csv/")
async def get_csv_results(experiment_name: str | None = None):
    if experiment_name is None:
        return {"experiment": "all", "results": "Here are the CSV results for all experiments!"}
    return {"experiment": experiment_name, "results": "Here are the CSV results for the experiment!"}

@router.get("/graph/")
async def get_graph_results(experiment_name: str | None = None, graph_type: str | None = None):
    if experiment_name is None:
        return {"experiment": "all", "results": "Here are the graph results for all experiments!"}
    if graph_type:
        return {"experiment": experiment_name, "results": f"Here are the {graph_type} graph results for the experiment!"}
    return {"experiment": experiment_name, "results": "Here are the graph results for the experiment!"}