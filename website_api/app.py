from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from website_api.client import get_control_api_base_url
from website_api.routes import router


app = FastAPI(title="Engine Simulator Website API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {
        "message": "Welcome to the Website API!",
        "control_api_base_url": get_control_api_base_url(),
    }